# Dual-Output Equalizer Implementation Proposal for Beocreate Frontend

## Current Architecture Analysis

After analyzing the current audio setup and available equalizer implementations, I've discovered:

1. **Current Audio Routing**:
   - The `asound.conf` defines two separate audio paths:
     - `softvol_hifiberry` (directed to the HiFiBerry card)
     - `softvol_RaspberryAudioJack` (directed to the Raspberry Pi's built-in audio)
   - These are combined into a `dual` output that sends the same audio to both outputs
   - Each has independent volume controls (`bed` and `headphone`)

2. **Existing Equalizer Implementations**:
   - `alsa-eq`: A simple 10-band graphic equalizer that uses ALSA's `equal` plugin
     - Works by switching the default PCM device between regular and equalized output
     - Currently applies the same EQ settings to all audio outputs
     - Uses `amixer` with `equal` device to adjust frequency bands

   - `equaliser`: A more sophisticated parametric equalizer with DSP integration
     - Part of the Beocreate sound processing system
     - Allows per-channel configuration (a, b, c, d, l, r channels)
     - Supports complex filter types (peak, shelf, crossover)
     - Fully integrated with the Beocreate UI framework

## Implementation Options

### Option 1: Extend ALSA Equal Plugin With Multiple Instances

Create multiple ALSA Equal plugin instances in the `asound.conf`, one for each output path:

```
pcm.equal_hifiberry {
  type equal
  slave.pcm "plug:softvol_hifiberry"
}

pcm.equal_raspberryaudio {
  type equal
  slave.pcm "plug:softvol_RaspberryAudioJack"
}

pcm.dual_eq {
  type plug
  slave {
    pcm {
      type multi
      slaves {
        a { pcm "equal_raspberryaudio" channels 2 }
        b { pcm "equal_hifiberry" channels 2 }
      }
      bindings {
        0 { slave a channel 0 }
        1 { slave a channel 1 }
        2 { slave b channel 0 }
        3 { slave b channel 1 }
      }
    }
    channels 4
  }
  ttable.0.0 1
  ttable.0.2 1
  ttable.1.1 1
  ttable.1.3 1
}
```

**Implementation Details**:
- Modify `alsa-mode` script to support multiple EQ modes/combinations
- Extend `alsa-eq` extension to manage both equalizers separately
- Add a tab or toggle in the UI to switch between HiFiBerry and Raspberry Pi equalizer settings

**Pros**:
- Simpler implementation using existing ALSA tools
- Works with any audio player software
- No need for custom DSP programming

**Cons**:
- Limited to fixed 10-band graphic EQ
- May introduce additional latency with multiple EQ processing stages
- Requires ALSA reconfiguration when switching between modes

## Implementation Plan

1. **ALSA Configuration**:
   - Modify `asound.conf` to create separate equalizer instances for each output
   - Create a new multi-device that combines both equalized outputs

2. **ALSA Mode Script**:
   - Extend `alsa-mode` to support multiple equalizer modes:
     - `EQUAL_ALL`: Apply equalizer to both outputs
     - `EQUAL_HIFIBERRY`: Apply equalizer only to HiFiBerry
     - `EQUAL_RASPBERRYPI`: Apply equalizer only to Raspberry Pi output
     - `SOFTVOL`: No equalization (current default)

3. **Frontend Extension**:
   - Fork the existing `alsa-eq` extension to create `dual-eq`
   - Add a tab selector to toggle between "HiFiBerry EQ" and "Raspberry Pi EQ"
   - Maintain separate settings objects for each output
   - Update the backend code to send commands to the appropriate equalizer

4. **Backend Implementation**:
   - Create new amixer control functions that target the specific equalizer instance
   - Implement state management to remember settings for both equalizers
   - Add functions to switch between equalizer modes

5. **UI Improvements**:
   - Add visual indication of which output is being configured
   - Provide presets that can be applied to either or both outputs
   - Include a "link" option to apply the same settings to both outputs

## Conclusion

The dual-output equalizer implementation will enhance the Beocreate system by allowing independent sound shaping for both the HiFiBerry DAC and the Raspberry Pi's built-in audio jack.

The implementation builds on the existing codebase and follows the established patterns in the Beocreate ecosystem, making it maintainable and consistent with the rest of the system.