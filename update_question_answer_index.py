from pathlib import Path
import re

import pdfplumber


ROOT = Path(__file__).resolve().parent
PDF_PATH = Path(
    r"d:\work\E02\Real-Time Networks Communication and Security for Autonomous Systems\cc meetings\CO1_CO2_All_Questions.pdf"
)
NOTES_PATH = ROOT / "outputs" / "CO1_CO2_Solved_Notes.md"

START = "<!-- BEGIN COMPLETE PDF QUESTION ANSWER INDEX -->"
END = "<!-- END COMPLETE PDF QUESTION ANSWER INDEX -->"


def extract_questions() -> list[tuple[str, str]]:
    questions: list[tuple[str, str]] = []
    co: str | None = None
    buffer: list[str] = []
    continuation_starts = (
        "Show all intermediate calculations",
        "Illustrate the answer",
        "Apply the selected communication or scheduling method",
        "Solve all intermediate steps",
    )

    with pdfplumber.open(PDF_PATH) as pdf:
        for page in pdf.pages:
            text = page.extract_text(x_tolerance=1, y_tolerance=3) or ""
            for raw_line in text.splitlines():
                line = raw_line.strip()
                if not line:
                    continue
                if line in {"CO1", "CO2"}:
                    co = line
                    continue
                if not buffer and questions and line.startswith(continuation_starts):
                    last_co, last_question = questions[-1]
                    questions[-1] = (last_co, f"{last_question} {line}")
                    continue
                buffer.append(line)
                if line.endswith("."):
                    questions.append((co or "Unknown", " ".join(buffer)))
                    buffer = []

    if buffer:
        questions.append((co or "Unknown", " ".join(buffer)))

    return questions


def latency_answer(transmit: str, receive: str, result: str) -> str:
    return f"""**Definition:** Latency is the one-way communication delay between the time a packet is transmitted and the time it is received.

**Formula:**

```text
Latency = receive time - transmit time
```

**Given data:**

```text
Transmit time = {transmit} ms
Receive time = {receive} ms
```

**Calculation:**

```text
Latency = {receive} - {transmit}
Latency = {result} ms
```

**Block diagram:**

```text
[Sensor node] -- packet transmitted at {transmit} ms --> [Network] -- received at {receive} ms --> [Controller]
                                      <----------- latency = {result} ms ----------->
```

**Interpretation:** The packet takes **{result} ms** to travel from the sensor to the controller. Lower latency gives the autonomous controller more time to decide and actuate before its deadline."""


def packet_metric_answer(
    latencies: list[int],
    bits: int | None,
    seconds: float | None,
    suffix: str = "",
) -> str:
    avg = sum(latencies) / len(latencies)
    jitter_value = max(latencies) - min(latencies)
    latency_text = " + ".join(str(item) for item in latencies)
    lines = [
        "**Definitions:**",
        "",
        "- Average latency is the mean packet delay.",
        "- Jitter is the variation in packet delay. Here, jitter = maximum latency - minimum latency.",
        "- Throughput is the amount of data successfully transmitted per second.",
        "",
        "**Block diagram:**",
        "",
        "```text",
        "[Sender] -> [Network path with variable delay] -> [Receiver]",
        "              |",
        f"              +-- observed packet latencies: {', '.join(str(x) + ' ms' for x in latencies)}",
        "```",
        "",
        "**Given data:**",
        "",
        "```text",
        f"Latencies = {', '.join(str(x) + ' ms' for x in latencies)}",
    ]
    if bits is not None and seconds is not None:
        lines.extend([f"Total data = {bits:,} bits", f"Transmission time = {seconds:g} s"])
    lines.extend(
        [
            "```",
            "",
            "**Average latency calculation:**",
            "",
            "```text",
            f"Average latency = ({latency_text}) / {len(latencies)}",
            f"Average latency = {sum(latencies)} / {len(latencies)}",
            f"Average latency = {avg:g} ms",
            "```",
            "",
            "**Jitter calculation:**",
            "",
            "```text",
            "Jitter = maximum latency - minimum latency",
            f"Jitter = {max(latencies)} - {min(latencies)}",
            f"Jitter = {jitter_value} ms",
            "```",
        ]
    )
    if bits is not None and seconds is not None:
        throughput_bps = bits / seconds
        throughput_mbps = throughput_bps / 1_000_000
        lines.extend(
            [
                "",
                "**Throughput calculation:**",
                "",
                "```text",
                "Throughput = total bits / total time",
                f"Throughput = {bits:,} / {seconds:g}",
                f"Throughput = {throughput_bps:,.0f} bit/s",
                f"Throughput = {throughput_mbps:g} Mbps",
                "```",
                "",
                f"**Final answer:** average latency = **{avg:g} ms**, jitter = **{jitter_value} ms**, throughput = **{throughput_mbps:g} Mbps**.",
            ]
        )
    else:
        lines.extend(
            [
                "",
                f"**Final answer:** average latency = **{avg:g} ms**, jitter = **{jitter_value} ms**.",
            ]
        )
    lines.append(
        "**Interpretation:** Lower average latency improves reaction speed. Lower jitter improves predictability because packets arrive at more regular intervals."
        + suffix
    )
    return "\n".join(lines)


def throughput_jitter_packets_answer(suffix: str = "") -> str:
    return """**Definitions:**

- Throughput is the transmitted data rate in bits per second.
- Jitter is the variation in packet latency. Here, jitter = maximum latency - minimum latency.

**Block diagram:**

```text
[Sender] -- four 1,000-byte packets in 20 ms --> [Network] --> [Receiver]
                 packet delays: 4 ms, 5 ms, 7 ms, 6 ms
```

**Given data:**

```text
Number of packets = 4
Packet size = 1,000 bytes
Latencies = 4 ms, 5 ms, 7 ms, 6 ms
Transmission time = 20 ms = 0.020 s
```

**Data conversion:**

```text
Total bytes = 4 x 1,000 = 4,000 bytes
Total bits = 4,000 x 8 = 32,000 bits
```

**Throughput calculation:**

```text
Throughput = total bits / total time
Throughput = 32,000 / 0.020
Throughput = 1,600,000 bit/s
Throughput = 1.6 Mbps
```

**Jitter calculation:**

```text
Jitter = maximum latency - minimum latency
Jitter = 7 - 4
Jitter = 3 ms
```

**Final answer:** throughput = **1.6 Mbps**, jitter = **3 ms**.

**Interpretation:** The network can deliver 1.6 megabits per second for this sample. The delay variation is 3 ms, so packet timing is not perfectly uniform.""" + suffix


def task_timing_answer(release: int, start: int, completion: int, deadline: int, label: str) -> str:
    waiting = start - release
    execution = completion - start
    response = completion - release
    margin = deadline - completion
    status = "meets" if margin >= 0 else "misses"
    by = "before" if margin >= 0 else "after"
    return f"""**Definitions:**

- Waiting time is the time a released task waits before execution starts.
- Execution time is the time spent running on the processor.
- Response time is the total time from release to completion.
- Deadline margin is the remaining time between completion and the absolute deadline.

**Block diagram:**

```text
time ---->

Release       Start       Completion       Deadline
  |             |              |               |
  v             v              v               v
--+-------------+--------------+---------------+--
  <--- wait ---><-- execute -->
  <-------- response --------->
                                <--- margin --->
```

**Given data for the {label}:**

```text
Release time = {release} ms
Start time = {start} ms
Completion time = {completion} ms
Absolute deadline = {deadline} ms
```

**Calculations:**

```text
Waiting time = start - release = {start} - {release} = {waiting} ms
Execution time = completion - start = {completion} - {start} = {execution} ms
Response time = completion - release = {completion} - {release} = {response} ms
Deadline margin = deadline - completion = {deadline} - {completion} = {margin} ms
```

**Final answer:** waiting time = **{waiting} ms**, execution time = **{execution} ms**, response time = **{response} ms**, deadline margin = **{margin} ms**.

**Interpretation:** The task **{status}** the deadline because it completes {abs(margin)} ms {by} the deadline."""


def deadline_miss_answer() -> str:
    return """**Definition:** Deadline margin shows whether a task finishes before or after its absolute deadline.

**Formula:**

```text
Deadline margin = absolute deadline - completion time
```

**Block diagram:**

```text
time ---->
Deadline at 15 ms        Completion at 18 ms
      |                         |
------+-------------------------+--
      <------ task is late by 3 ms ------>
```

**Calculation:**

```text
Deadline margin = 15 - 18
Deadline margin = -3 ms
```

**Final answer:** The task misses its deadline by **3 ms**.

**Interpretation:** For a hard real-time task, this is a timing failure. For a soft real-time task, the result may still be usable but with reduced value."""


def throughput_only_answer(suffix: str = "") -> str:
    return """**Definition:** Throughput is the amount of data transmitted successfully per unit time.

**Block diagram:**

```text
[Sender] -- 120 packets, 1,000 bytes each, over 0.4 s --> [Receiver]
```

**Given data:**

```text
Packets = 120
Packet size = 1,000 bytes
Transmission time = 0.4 s
```

**Data conversion:**

```text
Total bytes = 120 x 1,000 = 120,000 bytes
Total bits = 120,000 x 8 = 960,000 bits
```

**Calculation:**

```text
Throughput = total bits / total time
Throughput = 960,000 / 0.4
Throughput = 2,400,000 bit/s
Throughput = 2.4 Mbps
```

**Final answer:** throughput = **2.4 Mbps**.

**Interpretation:** This network sample carries 2.4 megabits per second.""" + suffix


def can_answer(order: list[str]) -> str:
    return f"""**Definition:** CAN arbitration decides which simultaneous frame gets bus access first. A lower CAN identifier has higher priority.

**Rule:**

```text
Lower identifier value -> higher priority -> transmits earlier
```

**Block diagram:**

```text
[CAN node A] --\
[CAN node B] ----> [CAN bus arbitration] -> [Winning frame first]
[CAN node C] --/
```

**Calculation method:** Sort the identifiers in ascending hexadecimal value.

```text
Transmission order = {' -> '.join(order)}
```

**Final answer:** **{' -> '.join(order)}**."""


def utilization_answer(kind: str, terms: list[tuple[str, int, int]], bound_text: str) -> str:
    pieces = [f"{c}/{t}" for _, c, t in terms]
    decimals = [c / t for _, c, t in terms]
    total = sum(decimals)
    percent = total * 100
    priority = sorted(terms, key=lambda item: item[2])
    priority_text = " -> ".join(name for name, _, _ in priority)
    return f"""**Definition:** Processor utilization is the fraction of processor time required by a periodic task set.

**Formula:**

```text
U = sum(Ci / Ti)
```

where `Ci` is execution time and `Ti` is period.

**Block diagram:**

```text
[Task set] -> [Compute each Ci/Ti] -> [Sum utilization] -> [Schedulability decision]
```

**Given data:**

```text
{chr(10).join(f'{name}: C = {c}, T = {t}' for name, c, t in terms)}
```

**Calculation:**

```text
U = {' + '.join(pieces)}
U = {' + '.join(f'{item:.3g}' for item in decimals)}
U = {total:.3g} = {percent:g}%
```

**Priority order:** {priority_text} for RMS, because shorter period means higher priority.

**Schedulability decision:** {bound_text}

**Final answer:** {kind} utilization = **{percent:g}%**; priority/order = **{priority_text}** where RMS priority is requested."""


def edf_jobs_answer() -> str:
    return """**Definition:** Earliest Deadline First schedules the ready job with the nearest absolute deadline.

**Block diagram:**

```text
[Ready jobs] -> [Compare absolute deadlines] -> [Run earliest deadline] -> [Repeat at next event]
```

**Given jobs:**

```text
J1: release = 0, execution = 2, deadline = 5
J2: release = 0, execution = 1, deadline = 3
J3: release = 1, execution = 2, deadline = 7
```

**Step-by-step schedule:**

```text
At t = 0: J1(D=5) and J2(D=3) are ready. Run J2 first.
J2 runs from 0 to 1 and completes before D=3.

At t = 1: J1(D=5) and J3(D=7) are ready. Run J1 next.
J1 runs from 1 to 3 and completes before D=5.

At t = 3: J3(D=7) remains. Run J3.
J3 runs from 3 to 5 and completes before D=7.
```

**Timeline:**

```text
0       1           3           5
|--J2--|----J1------|----J3------|
```

**Final answer:** execution order = **J2 -> J1 -> J3**, and all jobs meet their deadlines."""


def cycle_answer(title: str, windows: list[tuple[str, int, int]], interpretation: str) -> str:
    total = windows[-1][2]
    timeline = " ".join(f"{start}-{end} ms: {name}" for name, start, end in windows)
    return f"""**Definition:** A communication cycle divides time into fixed windows so traffic with different timing needs can be transmitted predictably.

**Block diagram:**

```text
[Traffic classes] -> [Scheduled cycle windows] -> [Deterministic transmission]
```

**Constructed {title}:**

```text
{timeline}
Total cycle time = {total} ms
```

**Timeline:**

```text
{' | '.join(f'{name} ({start}-{end} ms)' for name, start, end in windows)}
```

**Final answer:** The cycle is valid because all windows sum to **{total} ms**.

**Interpretation:** {interpretation}"""


def answer_for(question: str) -> str:
    q = question.lower()

    if "transmitted at 12.4 ms" in q:
        return latency_answer("12.4", "17.9", "5.5")
    if "four packets of 1,000 bytes" in q:
        suffix = ""
        if "satisfies the stated real-time requirement" in q:
            suffix = "\n\n**Requirement check:** No numeric real-time requirement is given in the question, so satisfaction cannot be confirmed. It is satisfactory only if the required throughput is <= 1.6 Mbps and the allowed jitter is >= 3 ms."
        return throughput_jitter_packets_answer(suffix)
    if "braking task is released at 2 ms" in q:
        return task_timing_answer(2, 5, 11, 15, "braking task")
    if "drone-control task is released at 10 ms" in q:
        return task_timing_answer(10, 13, 20, 24, "drone-control task")
    if "industrial robot task is released at 4 ms" in q:
        return task_timing_answer(4, 7, 14, 18, "industrial robot task")
    if "released at 1 ms" in q and "started at 4 ms" in q:
        return task_timing_answer(1, 4, 10, 13, "task")
    if "40,000 bits" in q:
        return packet_metric_answer([4, 6, 5, 7], 40_000, 0.010)
    if "48,000 bits" in q:
        return packet_metric_answer([3, 5, 4, 6], 48_000, 0.012)
    if "packet latencies of 4 ms, 6 ms, 5 ms and 5 ms" in q:
        return packet_metric_answer([4, 6, 5, 5], None, None)
    if "60,000 bits" in q:
        return packet_metric_answer([5, 7, 6, 8, 4], 60_000, 0.015)
    if "70,000 bits" in q:
        return packet_metric_answer([4, 6, 8, 5, 7], 70_000, 0.020)
    if "latencies of 6 ms, 8 ms, 7 ms and 9 ms" in q:
        return packet_metric_answer([6, 8, 7, 9], None, None)
    if "120 packets of 1,000 bytes" in q:
        suffix = ""
        if "satisfies the stated real-time requirement" in q:
            suffix = "\n\n**Requirement check:** No numeric requirement is stated, so satisfaction cannot be confirmed. It is satisfactory only if the required throughput is <= 2.4 Mbps."
        return throughput_only_answer(suffix)
    if "finishes at 18 ms" in q and "deadline is 15 ms" in q:
        return deadline_miss_answer()

    if "correctness of a real-time system" in q:
        return "Correctness depends on both logical output and time of completion. A correct value produced after the deadline is still a real-time failure, such as a braking command calculated after the collision window."
    if "airbag controller" in q and "video-streaming" in q:
        return "An automobile airbag controller is hard real-time because a missed deadline can cause injury. Online video streaming is soft real-time because delay mainly reduces quality."
    if "emergency braking, path planning, infotainment streaming and periodic data logging" in q:
        return "Emergency braking is hard real-time. Path planning, infotainment streaming, and periodic data logging are generally soft real-time unless they are directly tied to an immediate safety actuator."
    if "emergency braking, route planning, infotainment streaming, obstacle detection and system logging" in q:
        return "Emergency braking and immediate obstacle detection are hard real-time. Route planning, infotainment streaming, and system logging are usually soft real-time."
    if "hard and soft real-time systems" in q:
        return "Hard real-time systems have strict deadlines and deadline misses can invalidate the result or cause unsafe operation. Soft real-time systems tolerate occasional deadline misses with degraded quality. Hard systems require stronger predictability and analyzable scheduling."
    if "characteristics of autonomous systems" in q and ("predictable" in q or "low-latency" in q or "reliable" in q):
        return "They perform continuous sensing, closed-loop control, distributed coordination, and safety-critical actuation. Because the physical environment changes quickly, communication must be low-latency, low-jitter, reliable, and deadline-compliant. Example: a warehouse robot must receive obstacle data before it reaches the obstacle."
    if "warehouse robot" in q:
        return "It needs low latency for fast reaction, low jitter for stable control, enough throughput for sensor and status data, high reliability to avoid missing hazards, and deadline compliance for safety commands."
    if "timing constraint" in q:
        return "A timing constraint specifies when a task or message must complete. In autonomous systems, data and commands lose value after the deadline because the physical state may already have changed."
    if "response time and deadline" in q:
        return "Response time is completion time minus release time. A task is acceptable only if response time is within the allowed relative deadline, or equivalently if completion time is not later than the absolute deadline."
    if "event occurrence time" in q:
        return "Event occurrence is when the physical event happens; release time is when the software task becomes ready; start time is when execution begins; completion time is when it finishes; deadline is the latest allowed completion time."
    if "latency, jitter and throughput" in q and "compare" in q:
        return "Latency is packet delay, measured in time units. Jitter is variation in packet delay, also measured in time units. Throughput is delivered data rate, measured in bit/s. High latency delays decisions, high jitter makes timing unpredictable, and low throughput restricts sensor/video data."
    if "purpose of real-time communication" in q:
        return "Its purpose is to deliver sensor data, coordination data, and actuator commands within known time limits so an autonomous system can perceive, decide, and act before deadlines expire."
    if "contrast latency and jitter" in q:
        return "Latency is the delay of one packet or message. Jitter is the variation among packet delays. A system may have low average latency but still poor predictability if jitter is high."
    if "autonomous-braking example" in q:
        return "A real-time system is one where correctness depends on what result is produced and when it is produced. In autonomous braking, detecting an obstacle and computing the correct brake force is useful only if the brake command reaches the actuator before the stopping deadline."
    if "autonomous drone during sensing" in q:
        return "Sensing needs timely IMU, GPS, camera, and range data; navigation needs reliable position updates; obstacle avoidance needs hard real-time low latency; video needs high throughput; emergency landing needs highest-priority reliable deadline-compliant commands."

    if "time-triggered or event-triggered" in q and "wheel-speed" in q and "collision alerts" in q:
        return "Wheel-speed sensing and periodic battery monitoring should be time-triggered. Collision alerts and airbag activation should be event-triggered with highest priority. Diagnostic reporting can be event-triggered or scheduled as low-priority traffic."
    if "periodic transmission of wheel-speed" in q:
        return "Use time-triggered communication because wheel-speed data is periodic and should be transmitted at predictable intervals."
    if "sudden collision warning" in q:
        return "Use event-triggered communication because the message is generated by an unexpected safety event and must be sent immediately."
    if "emergency temperature alarm" in q:
        return "Use event-triggered communication because the alarm is generated only when the threshold is exceeded."
    if "periodic sensor messages" in q and "emergency braking" in q and "diagnostic" in q:
        return "Use time-triggered communication for periodic sensor messages, event-triggered high-priority communication for emergency braking, and low-priority event-triggered or scheduled communication for diagnostics."

    if "0x120 and 0x080" in q:
        return can_answer(["0x080", "0x120"])
    if "0x120, 0x080, 0x200 and 0x100" in q:
        return can_answer(["0x080", "0x100", "0x120", "0x200"])
    if "0x305, 0x105 and 0x205" in q:
        return can_answer(["0x105", "0x205", "0x305"])
    if "0x150, 0x090, 0x300 and 0x110" in q:
        return can_answer(["0x090", "0x110", "0x150", "0x300"])
    if "0x150, 0x090, 0x300, 0x110 and 0x070" in q:
        return can_answer(["0x070", "0x090", "0x110", "0x150", "0x300"])
    if "0x070 and 0x100" in q:
        return can_answer(["0x070", "0x100"])

    if "periods of 5 ms, 10 ms and 20 ms" in q:
        return "Under RMS, the shortest period has highest priority. Priority order is 5 ms -> 10 ms -> 20 ms."
    if "periods of 8 ms, 16 ms and 32 ms" in q:
        return "Under RMS, priority order is 8 ms -> 16 ms -> 32 ms."
    if "t1(c=1, t=10), t2(c=2, t=20) and t3(c=1, t=25)" in q:
        return utilization_answer("Processor", [("T1", 1, 10), ("T2", 2, 20), ("T3", 1, 25)], "U = 0.24 is below the RMS sufficient bound 0.779763 and below the EDF limit 1.0, so it is schedulable under these assumptions.")
    if "t1(c=1, t=5), t2(c=2, t=10) and t3(c=2, t=20)" in q:
        return utilization_answer("RMS", [("T1", 1, 5), ("T2", 2, 10), ("T3", 2, 20)], "U = 0.50 is below the 3-task RMS sufficient bound 0.779763, so the task set is schedulable by this test.")
    if "t1(c=1, t=4), t2(c=1, t=5) and t3(c=2, t=10)" in q:
        return utilization_answer("RMS", [("T1", 1, 4), ("T2", 1, 5), ("T3", 2, 10)], "U = 0.65 is below the 3-task RMS sufficient bound 0.779763, so the task set is schedulable by this test.")
    if "t1(c=1, t=5), t2(c=2, t=10) and t3(c=3, t=20)" in q:
        return utilization_answer("RMS", [("T1", 1, 5), ("T2", 2, 10), ("T3", 3, 20)], "U = 0.55 is below the 3-task RMS sufficient bound 0.779763, so the task set is schedulable by this test.")
    if "t1(c=1, t=4), t2(c=2, t=8) and t3(c=2, t=16)" in q:
        return utilization_answer("RMS", [("T1", 1, 4), ("T2", 2, 8), ("T3", 2, 16)], "U = 0.625 is below the 3-task RMS sufficient bound 0.779763, so the task set is schedulable by this test.")
    if "t1(c=1, t=4), t2(c=2, t=8) and t3(c=2, t=10)" in q:
        return utilization_answer("EDF", [("T1", 1, 4), ("T2", 2, 8), ("T3", 2, 10)], "For EDF with deadlines equal to periods, U = 0.70 <= 1.0, so the task set is schedulable.")
    if "t1(c=1, t=5), t2(c=1, t=10) and t3(c=2, t=20)" in q:
        return utilization_answer("EDF", [("T1", 1, 5), ("T2", 1, 10), ("T3", 2, 20)], "For EDF with deadlines equal to periods, U = 0.40 <= 1.0, so the task set is schedulable.")
    if "t1(c=1, t=5), t2(c=2, t=10) and t3(c=4, t=20)" in q:
        return utilization_answer("EDF", [("T1", 1, 5), ("T2", 2, 10), ("T3", 4, 20)], "For EDF with deadlines equal to periods, U = 0.60 <= 1.0, so the task set is schedulable.")
    if "j1(r=0, c=2, d=5)" in q:
        return edf_jobs_answer()

    if "periodic braking messages and occasional diagnostic messages" in q:
        return "Place periodic braking messages in the FlexRay static segment because they are deterministic and safety-critical. Place occasional diagnostic messages in the dynamic segment because they occur irregularly."
    if "braking, steering, camera and diagnostic messages" in q:
        return "Use the FlexRay static segment for periodic braking and steering control. Use the dynamic segment for diagnostics. Camera data is high bandwidth and is usually assigned to dynamic service or better handled by Ethernet/TSN depending on system design."
    if "periodic steering-control messages" in q:
        return "Use the FlexRay static segment because steering-control messages are periodic and safety-critical."
    if "10 ms flexray communication cycle" in q:
        return cycle_answer("10 ms FlexRay cycle", [("Braking", 0, 2), ("Steering", 2, 4), ("Sensor data", 4, 6), ("Diagnostic data", 6, 8), ("Idle", 8, 10)], "Safety-control messages are placed early in fixed windows, and idle time leaves timing slack.")
    if "5 ms tsn communication cycle" in q:
        return cycle_answer("5 ms TSN cycle", [("Safety control", 0, 1), ("Sensor data", 1, 3), ("Video", 3, 4), ("Best effort", 4, 5)], "Safety traffic gets a protected first slot before larger or less critical traffic.")
    if "4 ms tsn transmission cycle" in q:
        return cycle_answer("4 ms TSN cycle", [("Control", 0, 1), ("Video", 1, 3), ("Best effort", 3, 4)], "Control traffic is protected first, while video and best-effort traffic use the remaining cycle time.")
    if "brake-control traffic, camera traffic and maintenance traffic" in q:
        return "Use a scheduled high-priority TSN window for brake-control traffic, a reserved high-throughput window for camera traffic, and a best-effort or low-priority window for maintenance traffic."
    if "ieee 802.11, lte or 5g" in q and "small laboratory" in q:
        return "Choose IEEE 802.11 because a small laboratory needs local high-data-rate wireless coverage rather than wide-area cellular service."
    if "indoor robot communication" in q and "city-wide vehicle tracking" in q:
        return "Use IEEE 802.11 for indoor robot communication, LTE for city-wide vehicle tracking with moderate latency, and 5G for cooperative collision-warning or cooperative safety communication."
    if "tracking autonomous delivery vehicles across a city" in q:
        return "Choose LTE because the scenario emphasizes wide-area coverage and moderate latency."
    if "cooperative safety-message exchange" in q or "rapidly moving autonomous vehicles" in q:
        return "Choose 5G because cooperative safety communication among fast-moving vehicles requires low latency and high reliability."
    if "communication framework using can" in q:
        return "Use CAN for internal low-to-medium-rate sensors, FlexRay for deterministic safety control, TSN for scheduled Ethernet traffic, IEEE 802.11 for local access, and 5G for remote or cooperative wide-area connectivity."

    return "See the detailed solved section below for the complete answer."


def build_index(questions: list[tuple[str, str]]) -> str:
    lines = [
        START,
        "",
        "## Complete PDF Question-Answer Index",
        "",
        "Each question below is copied from the source PDF and followed by a direct answer. Detailed explanations, diagrams, block diagrams, flowcharts, case studies, and worked methods continue in the later notebook sections.",
        "",
    ]

    for _co, question in questions:
        lines.extend(
            [
                f"**Question:** {question}",
                "",
                "**Answer:**",
                "",
                answer_for(question),
                "",
                "---",
                "",
            ]
        )

    lines.append(END)
    return "\n".join(lines) + "\n"


def insert_or_replace_index(notes: str, index_text: str) -> str:
    if START in notes and END in notes:
        before = notes.split(START, 1)[0].rstrip()
        after = notes.split(END, 1)[1].lstrip()
        return before + "\n\n" + index_text + "\n" + after

    anchor = "## Assumptions Used"
    if anchor not in notes:
        raise ValueError(f"Could not find insertion anchor: {anchor}")
    before, after = notes.split(anchor, 1)
    return before.rstrip() + "\n\n" + index_text + "\n" + anchor + after


def remove_visible_numbered_headings(notes: str) -> str:
    return re.sub(r"(?m)^###\s+\d+\.\s+", "### ", notes)


def main() -> None:
    questions = extract_questions()
    index_text = build_index(questions)
    notes = NOTES_PATH.read_text(encoding="utf-8")
    updated = insert_or_replace_index(notes, index_text)
    updated = remove_visible_numbered_headings(updated)
    NOTES_PATH.write_text(updated, encoding="utf-8", newline="\n")

    print(f"Extracted questions: {len(questions)}")
    print(f"Wrote: {NOTES_PATH}")


if __name__ == "__main__":
    main()
