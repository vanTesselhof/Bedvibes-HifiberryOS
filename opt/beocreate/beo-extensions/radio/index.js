var version = require("./package.json").version;
var exec    = require( 'child_process' ).exec;
var TuneIn  = require( 'node-tunein-radio');

var debug = beo.debug;

var defaultSettings = { "favourites": {} };
var settings = JSON.parse(JSON.stringify(defaultSettings));

var search_results;
var found_stations = {};

var tunein = new TuneIn({
    protocol        : 'https',          
    cacheRequests   : true,             
    cacheTTL        : 1000 * 60 * 30,   
    partnerId       : 'no default'      
});

beo.bus.on('general', function(event) {
	if (event.header == "activatedExtension") {
		if (event.content.extension == "radio") {
			beo.sendToUI("radio", {
				header: "homeContent", 
				content: {
					favourites: settings.favourites 
				}
			});
		}
	}
});

beo.bus.on('radio', function(event) {
	switch (event.header) {
		case "settings":
			if (event.content.settings) {
				settings = Object.assign(settings, event.content.settings);
			}

			break;
		case "search":
			var query = event.content;
			tunein.search(query).then(function(result) {

				search_results = result.body;
				found_stations = {};
				
				for (i in search_results) {
					if (search_results[i].item && search_results[i].item == "station") {
						if (search_results[i].formats && search_results[i].formats !== "wma") {
							found_stations[search_results[i].guide_id] = search_results[i];
							if (settings.favourites[search_results[i].guide_id]) {
								found_stations[search_results[i].guide_id].isFavourite = true;
							} else {
								found_stations[search_results[i].guide_id].isFavourite = false;
							}
						}
					}
				}

				beo.sendToUI("radio", {header: "searchResults", content: { found_stations }});

			}).catch(function(err) {
				if (err) {
					if (debug) console.log(err);
				}
			})

			break;
		case "play":
			exec('/opt/hifiberry/bin/start-radio "'+ event.content.URL +'" "'+event.content.stationName+'"', 
				function(error, stdout, stderr) {
					if (error) {
						if (debug) console.error("Starting radio failed: "+error, stderr);
						} else {
						if (debug) console.log("Starting radio finished.", stdout);
						}
				}
			)

			if (beo.extensions.sources && beo.extensions.sources.setSourceOptions) {
			    beo.extensions.sources.setSourceOptions("radio", {
				    aliasInNowPlaying: event.content.stationName
			    }, true);
			}

			break;
		case "add-to-favourite":
			if (!settings.favourites[event.content.stationId]) {
				settings.favourites[event.content.stationId] = {
					title: found_stations[event.content.stationId].text,
					img: found_stations[event.content.stationId].image,
					url: found_stations[event.content.stationId].URL
				}
				isFavourite = true;
			} else {
				delete settings.favourites[event.content.stationId]
				isFavourite = false;
			}

			beo.sendToUI("radio", {
				header: "stationFavourited", 
				content: { 
					guide_id: event.content.stationId, 
					isFavourite: isFavourite 
				}
			});
			beo.sendToUI("radio", {
				header: "homeContent", 
				content: {
					favourites: settings.favourites 
				}
			});
			beo.saveSettings("radio", settings);

			break;
	}
});

function checkMPDStatus(callback) {
	if (beo.extensions.mpd && beo.extensions.mpd.isEnabled) {
		beo.extensions.mpd.isEnabled(callback);
	}
}

module.exports = {
	version: version,
	isEnabled: checkMPDStatus
};
