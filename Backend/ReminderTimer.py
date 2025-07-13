import threading
from datetime import datetime, timedelta
import time
import re
import os
import json

# Global storage for active reminders and timers
active_reminders = []
active_timers = []

# JSON file paths for persistent storage
REMINDERS_FILE = os.path.join(os.getcwd(), "Data", "reminders.json")
TIMERS_FILE = os.path.join(os.getcwd(), "Data", "timers.json")

# Ensure Data directory exists
os.makedirs(os.path.dirname(REMINDERS_FILE), exist_ok=True)


# JSON Storage Functions
def save_reminders():
    """Save reminders to JSON file"""
    try:
        reminders_data = []
        for reminder in active_reminders:
            reminder_copy = reminder.copy()
            reminder_copy["time"] = reminder_copy["time"].isoformat()
            reminders_data.append(reminder_copy)

        with open(REMINDERS_FILE, "w", encoding="utf-8") as f:
            json.dump(reminders_data, f, indent=2)
    except Exception as e:
        print(f"Error saving reminders: {e}")


def load_reminders():
    """Load reminders from JSON file"""
    global active_reminders
    try:
        if os.path.exists(REMINDERS_FILE):
            with open(REMINDERS_FILE, "r", encoding="utf-8") as f:
                reminders_data = json.load(f)

            active_reminders = []
            current_time = datetime.now()

            for reminder_data in reminders_data:
                reminder_time = datetime.fromisoformat(reminder_data["time"])

                # Only load future reminders
                if reminder_time > current_time:
                    reminder_data["time"] = reminder_time
                    active_reminders.append(reminder_data)

                    # Restart the reminder worker thread
                    threading.Thread(
                        target=reminder_worker, args=(reminder_data,), daemon=True
                    ).start()

            # Save cleaned up reminders (remove past ones)
            save_reminders()
    except Exception as e:
        print(f"Error loading reminders: {e}")


def save_timers():
    """Save timers to JSON file"""
    try:
        timers_data = []
        for timer in active_timers:
            timer_copy = timer.copy()
            timer_copy["start_time"] = timer_copy["start_time"].isoformat()
            timer_copy["end_time"] = timer_copy["end_time"].isoformat()
            timers_data.append(timer_copy)

        with open(TIMERS_FILE, "w", encoding="utf-8") as f:
            json.dump(timers_data, f, indent=2)
    except Exception as e:
        print(f"Error saving timers: {e}")


def load_timers():
    """Load timers from JSON file"""
    global active_timers
    try:
        if os.path.exists(TIMERS_FILE):
            with open(TIMERS_FILE, "r", encoding="utf-8") as f:
                timers_data = json.load(f)

            active_timers = []
            current_time = datetime.now()

            for timer_data in timers_data:
                end_time = datetime.fromisoformat(timer_data["end_time"])

                # Only load active timers
                if end_time > current_time:
                    timer_data["start_time"] = datetime.fromisoformat(
                        timer_data["start_time"]
                    )
                    timer_data["end_time"] = end_time

                    # Calculate remaining duration
                    remaining_seconds = (end_time - current_time).total_seconds()
                    if remaining_seconds > 0:
                        # Update the timer with remaining duration
                        timer_data["duration"] = int(remaining_seconds)
                        active_timers.append(timer_data)

                        # Restart the timer worker thread
                        threading.Thread(
                            target=timer_worker, args=(timer_data,), daemon=True
                        ).start()

            # Save cleaned up timers (remove expired ones)
            save_timers()
    except Exception as e:
        print(f"Error loading timers: {e}")


def initialize_storage():
    """Initialize storage by loading existing reminders and timers"""
    load_reminders()
    load_timers()


# Function to speak reminder/timer notifications
def speak_notification(message):
    """Function to trigger text-to-speech for notifications"""
    try:
        from .TextToSpeech import textToSpeech

        textToSpeech(message)
    except ImportError:
        try:
            with open(
                rf"{os.getcwd()}\Frontend\Files\Responses.data", "w", encoding="utf-8"
            ) as file:
                file.write(message)
        except:
            print(f"Notification: {message}")


# Function to parse time from user input
def parse_time(time_text):
    """Parse time from natural language input"""
    time_text = time_text.lower().strip()

    # Handle specific time formats like "9 pm", "9:30 pm", "21:00"
    time_patterns = [
        r"(\d{1,2}):(\d{2})\s*(am|pm)",  # 9:30 pm
        r"(\d{1,2})\s*(am|pm)",  # 9 pm
        r"(\d{1,2}):(\d{2})",  # 21:00, 09:30
        r"at\s*(\d{1,2}):(\d{2})\s*(am|pm)",  # at 9:30 pm
        r"at\s*(\d{1,2})\s*(am|pm)",  # at 9 pm
    ]

    for pattern in time_patterns:
        match = re.search(pattern, time_text)
        if match:
            try:
                if len(match.groups()) == 3:  # Hour, minute, am/pm
                    hour = int(match.group(1))
                    minute = int(match.group(2))
                    period = match.group(3)

                    if period == "pm" and hour != 12:
                        hour += 12
                    elif period == "am" and hour == 12:
                        hour = 0

                elif len(match.groups()) == 2:
                    if match.group(2) in ["am", "pm"]:  # Hour, am/pm
                        hour = int(match.group(1))
                        minute = 0
                        period = match.group(2)

                        if period == "pm" and hour != 12:
                            hour += 12
                        elif period == "am" and hour == 12:
                            hour = 0
                    else:  # Hour, minute (24-hour format)
                        hour = int(match.group(1))
                        minute = int(match.group(2))

                # Create target datetime for today at specified time
                now = datetime.now()
                target_time = now.replace(
                    hour=hour, minute=minute, second=0, microsecond=0
                )

                # If time has passed today, schedule for tomorrow
                if target_time <= now:
                    target_time += timedelta(days=1)

                return target_time
            except ValueError:
                continue

    return None


# Function to parse timer duration
def parse_timer_duration(duration_text):
    """Parse timer duration from natural language input"""
    duration_text = duration_text.lower().strip()

    # Patterns for different time units (ordered from most specific to least specific)
    patterns = [
        (r"(\d+)\s*hours?\b", "hours"),
        (r"(\d+)\s*minutes?\b", "minutes"),
        (r"(\d+)\s*seconds?\b", "seconds"),
        (r"(\d+)\s*mins?\b", "minutes"),
        (r"(\d+)\s*secs?\b", "seconds"),
        (r"(\d+)\s*h\b", "hours"),
        (r"(\d+)\s*m\b", "minutes"),
        (r"(\d+)\s*s\b", "seconds"),
    ]

    total_seconds = 0
    matched_positions = set()  # Track which parts of the string we've already matched

    for pattern, unit in patterns:
        matches = re.finditer(pattern, duration_text)
        for match in matches:
            # Skip if this position was already matched by a more specific pattern
            start, end = match.span()
            if any(pos in range(start, end) for pos in matched_positions):
                continue

            # Add positions to matched set
            matched_positions.update(range(start, end))

            value = int(match.group(1))
            if unit == "hours":
                total_seconds += value * 3600
            elif unit == "minutes":
                total_seconds += value * 60
            elif unit == "seconds":
                total_seconds += value

    return total_seconds if total_seconds > 0 else None


# Function to set a reminder
def set_reminder(command):
    """Set a reminder based on user command"""
    try:
        # Extract the reminder message and time
        command = command.lower()

        # Handle "reminder" format from Model.py (e.g., "reminder 9:00pm call mom")
        if command.startswith("reminder "):
            # Remove "reminder " prefix
            remainder = command.replace("reminder ", "", 1).strip()

            # Split by common time patterns to separate time from message
            time_patterns = [
                r"(\d{1,2}:?\d{0,2}\s*(?:am|pm))",  # 9pm, 9:30pm, etc.
                r"(\d{1,2}:?\d{0,2})",  # 21:00, 9, etc.
            ]

            time_text = ""
            reminder_text = ""

            for pattern in time_patterns:
                match = re.search(pattern, remainder)
                if match:
                    time_text = match.group(1)
                    # Everything after the time is the message
                    reminder_text = remainder.replace(time_text, "", 1).strip()
                    break

            if not time_text:
                # If no time pattern found, try to extract first word as time
                parts = remainder.split(" ", 1)
                if len(parts) >= 2:
                    time_text = parts[0]
                    reminder_text = parts[1]
                else:
                    return "Please specify a time for the reminder (e.g., '9 PM')"

        else:
            # Handle "remind me" format (original logic)
            # Find time-related keywords
            time_keywords = ["at", "on", "by"]
            reminder_text = ""
            time_text = ""

            # Split command to find time part
            for keyword in time_keywords:
                if keyword in command:
                    parts = command.split(keyword, 1)
                    if len(parts) == 2:
                        reminder_text = parts[0].strip()
                        time_text = parts[1].strip()
                        break

            if not time_text:
                return "Please specify a time for the reminder (e.g., 'at 9 PM')"

            # Remove common prefixes
            reminder_text = (
                reminder_text.replace("remind me", "").replace("that", "").strip()
            )

        # Parse the time
        target_time = parse_time(time_text)
        if not target_time:
            return "I couldn't understand the time format. Please use formats like '9 PM', '9:30 PM', or '21:00'"

        # Create reminder object
        reminder = {
            "id": len(active_reminders) + 1,
            "message": reminder_text,
            "time": target_time,
            "original_command": command,
        }

        active_reminders.append(reminder)

        # Save to JSON file
        save_reminders()

        # Start reminder thread
        threading.Thread(target=reminder_worker, args=(reminder,), daemon=True).start()

        time_str = target_time.strftime("%I:%M %p on %B %d")
        return f"Reminder set! I'll remind you '{reminder_text}' at {time_str}"

    except Exception as e:
        return f"Error setting reminder: {str(e)}"


# Function to set a timer
def set_timer(command):
    """Set a timer based on user command"""
    try:
        # Extract duration from command
        command = (
            command.lower()
            .replace("set a timer for", "")
            .replace("timer for", "")
            .strip()
        )

        duration_seconds = parse_timer_duration(command)
        if not duration_seconds:
            return "I couldn't understand the timer duration. Please use formats like '5 minutes', '30 seconds', or '1 hour'"

        # Create timer object
        timer = {
            "id": len(active_timers) + 1,
            "duration": duration_seconds,
            "start_time": datetime.now(),
            "end_time": datetime.now() + timedelta(seconds=duration_seconds),
        }

        active_timers.append(timer)

        # Save to JSON file
        save_timers()

        # Start timer thread
        threading.Thread(target=timer_worker, args=(timer,), daemon=True).start()

        # Format duration for response
        hours = duration_seconds // 3600
        minutes = (duration_seconds % 3600) // 60
        seconds = duration_seconds % 60

        duration_str = ""
        if hours > 0:
            duration_str += f"{hours} hour{'s' if hours != 1 else ''} "
        if minutes > 0:
            duration_str += f"{minutes} minute{'s' if minutes != 1 else ''} "
        if seconds > 0:
            duration_str += f"{seconds} second{'s' if seconds != 1 else ''}"

        return f"Timer set for {duration_str.strip()}. I'll notify you when it's done!"

    except Exception as e:
        return f"Error setting timer: {str(e)}"


# Worker function for reminders
def reminder_worker(reminder):
    """Background worker that waits for reminder time and triggers notification"""
    try:
        current_time = datetime.now()
        wait_seconds = (reminder["time"] - current_time).total_seconds()

        if wait_seconds > 0:
            time.sleep(wait_seconds)

            # Get username from environment
            username = os.environ.get("USERNAME", "User")

            # Create notification message
            time_str = reminder["time"].strftime("%I:%M %p")
            message = f"{username}, it's {time_str}. {reminder['message']}"

            # Trigger notification
            speak_notification(message)

            # Remove from active reminders
            if reminder in active_reminders:
                active_reminders.remove(reminder)
                save_reminders()  # Update JSON file

        # Save reminders to JSON file
        save_reminders()

    except Exception as e:
        print(f"Error in reminder worker: {e}")


# Worker function for timers
def timer_worker(timer):
    """Background worker that waits for timer duration and triggers notification"""
    try:
        time.sleep(timer["duration"])

        # Trigger notification
        speak_notification("Your timer is up!")

        # Remove from active timers
        if timer in active_timers:
            active_timers.remove(timer)
            save_timers()  # Update JSON file

        # Save timers to JSON file
        save_timers()

    except Exception as e:
        print(f"Error in timer worker: {e}")


# Function to list active reminders
def list_reminders():
    """List all active reminders"""
    if not active_reminders:
        return "You have no active reminders."

    result = "Your active reminders:\n"
    for reminder in active_reminders:
        time_str = reminder["time"].strftime("%I:%M %p on %B %d")
        result += f"• {reminder['message']} at {time_str}\n"

    return result.strip()


# Function to list active timers
def list_timers():
    """List all active timers"""
    if not active_timers:
        return "You have no active timers."

    result = "Your active timers:\n"
    for timer in active_timers:
        remaining = (timer["end_time"] - datetime.now()).total_seconds()
        if remaining > 0:
            minutes = int(remaining // 60)
            seconds = int(remaining % 60)
            result += f"• Timer ending in {minutes}m {seconds}s\n"

    return result.strip()


# Function to cancel reminders
def cancel_reminder(reminder_id=None):
    """Cancel a specific reminder or all reminders"""
    global active_reminders

    if reminder_id:
        for reminder in active_reminders:
            if reminder["id"] == reminder_id:
                active_reminders.remove(reminder)
                save_reminders()  # Update JSON file
                return f"Reminder {reminder_id} cancelled."
        return f"Reminder {reminder_id} not found."
    else:
        count = len(active_reminders)
        active_reminders.clear()
        save_reminders()  # Update JSON file
        return f"All {count} reminders cancelled."


# Function to cancel timers
def cancel_timer(timer_id=None):
    """Cancel a specific timer or all timers"""
    global active_timers

    if timer_id:
        for timer in active_timers:
            if timer["id"] == timer_id:
                active_timers.remove(timer)
                save_timers()  # Update JSON file
                return f"Timer {timer_id} cancelled."
        return f"Timer {timer_id} not found."
    else:
        count = len(active_timers)
        active_timers.clear()
        save_timers()  # Update JSON file
        return f"All {count} timers cancelled."


# Initialize storage when module is imported
initialize_storage()
