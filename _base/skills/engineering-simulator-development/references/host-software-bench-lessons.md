# Host-Software Bench Lessons

Load this reference when an emulator is used not to visualize a device but to **reproduce a defect in the production client software** without hardware: memory growth, freezes, throughput cliffs, reconnect storms.

## Replay Beats A Synthetic Scene

- Capture raw bytes from the real device and replay them. A procedural scene loads the client's parser and renderer differently, and any divergence from the hardware run then gets excused as "different data".
- Verify the replay reproduces the measured wire numbers of the real device — bytes per second, frames per second, mean frame size — and state both sets side by side before drawing conclusions.
- Keep the capture out of the repository; commit the capture tool and the measured baseline numbers instead.

## Give The Emulator An Explicit Rate Knob

- Deriving the emission rate from a modelled subsystem (motor RPM, encoder) collides with integer millisecond timers and coarse OS timer granularity. A 12.5 ms target rounds to 13 ms and delivers ~7 % less load than the device.
- Add a direct packets-per-second control that bypasses the model, and accumulate the emission debt from **measured elapsed time**, not from the number of timer ticks. Cap the per-tick burst so a delayed timer does not fire a spike the device never produces.
- Label the knob as a bench control in the UI and docs. Decoupling rate from the modelled subsystem is exactly what separates the experiment from life, and that must stay visible.

## Bound Every Producer-To-GUI Queue

- A worker thread that emits batches to the GUI over a queued connection (Qt `Qt::QueuedConnection`, or any post-to-event-loop scheme) has **no back pressure by default**. Each queued batch retains its own copy of the payload.
- While the GUI keeps up the queue is empty and invisible. The moment the GUI stalls, the queue grows at the full arrival rate; measured once at 43.7 MB/s, reaching multi-GB commit within minutes.
- The signature is diagnostic: **committed memory far above working set**. Payload written once by the producer and never read again gets paged out, so a normal leak (committed ≈ resident) looks different from a queue runaway.
- Bound the queue in units of **stream time**, not batch count, and size it by measurement. Too tight drops data during ordinary redraw jitter; too loose defeats the purpose. Roughly two seconds of stream is a good starting point.
- Dropping the newest batch is correct for a live view — stale points are worthless — but count what was dropped and show it, separately from network loss. Silent loss is worse than visible loss.
- Check what else feeds off the dropped path. If recording or logging is assembled downstream of the GUI, a dropped batch never reaches the file either; say so explicitly rather than letting the recording quietly thin out.

## Measure The Lag From The Producer Side

- A stalled consumer cannot report on itself. Any counter, log, or timer living in the GUI thread goes silent exactly at the moment the measurement is needed.
- Put the lag counters and their periodic dump in the producer thread. Use atomics with a single writer per counter; the consumer only decrements the in-flight count when it takes a batch.
- Decrement on **taking** the batch, not on finishing with it: the queue slot is freed by removal, and holding it for the duration of the work double-counts.

## Compare With One Binary, Not Two

- Expose the parameter under test as a bench override (environment variable is enough) so the old and new behavior can be produced by the **same executable**. Two builds can differ in ways nobody enumerated, and a reviewer is entitled to say so.
- Reproduce the trigger deterministically instead of waiting for it. Suspending the consumer thread for a fixed interval stands in for whatever froze it, and the fix must hold regardless of the cause.

## Same-Machine Emulator Networking

- Client software that binds its socket to a chosen NIC address, or pins the outbound interface, cannot reach another address of the same machine: the connect fails outright or hangs until timeout.
- When the client has a "device is on this computer" mode, that mode must also **drop the local bind and the interface pinning**, not just relax address-equality checks. Otherwise the mode advertises support it does not deliver.
- Prefer fixing that mode over adding host addresses to adapters: adding an IP needs administrator rights and changes system network configuration for a test.
