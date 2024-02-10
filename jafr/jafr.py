import os
import sys
import json
import datetime
import re


def display_user_menu():
    print("What would you like to do?")
    print("1. Complete tasks")
    print("2. Add a new meeting.")
    print("3. Share a task.")
    print("4. Share a meeting.")
    print("5. Change Jafr's master directory.")
    print("6. Exit")


def display_reminders(tasks, meetings):
    # Display tasks and meetings
    display_tasks_today(tasks)
    display_tasks_upcoming(tasks)
    display_meetings_today(meetings)
    display_meetings_upcoming_week(meetings)
    print()

def display_tasks_today(tasks):
    """Display tasks that are due today and are not completed."""
    print("Just a friendly reminder! You have these tasks to finish today.")
    today = datetime.date.today().strftime('%d/%m/%y')
    for task in tasks:
        if today in task and 'not complete' in task:
            description_part = task.split('Due:')[0]
            description = description_part.strip('- ').strip()
            print(f"- {description}")


def display_tasks_upcoming(tasks):
    """Display tasks that are due in the upcoming three days."""
    print("\nThese tasks need to be finished in the next three days!")
    today = datetime.date.today()
    for task in tasks:
        for day_delta in range(1, 4):  # Next 3 days
            check_date = (today + datetime.timedelta(days=day_delta)).strftime('%d/%m/%y')
            if check_date in task and 'not complete' in task:
                # print(f"task:{task}")
                try:
                    description, due_date = task.split('Due:')
                    due_date = due_date.split()
                    # print(f"due_date: {due_date}")
                    description = description.strip()
                    print(f"{description} by {due_date[0]}")
                except ValueError:
                    pass
                

def display_meetings_today(meetings):
    """Display meetings scheduled for today."""
    print("\nYou have the following meetings today!")
    today = datetime.date.today().strftime('%d/%m/%y')
    time_pattern = re.compile(r'\b\d{1,2}:\d{2}\b$')  # Matches HH:MM format at the end of a string

    for meeting in meetings:
        if today in meeting:
            if 'Scheduled:' not in meeting:
                print(f"Warning: The following meeting entry is not formatted correctly: {meeting.strip()}")
                continue
            description_part, time_date_part = meeting.split('Scheduled:')
            description = description_part.strip('- ').strip()
            time, date = time_date_part.strip().split()
            
            if time_pattern.fullmatch(time):   # check if time matches the HH:MM format
                print(f"- {description} at {time}")
           

def display_meetings_upcoming_week(meetings):
    """Display meetings for the upcoming week."""
    print("\nYou have the following meetings scheduled over the next week!")
    today = datetime.date.today()
    for meeting in meetings:
        for day_delta in range(1, 8):  # Next 7 days
            check_date = (today + datetime.timedelta(days=day_delta)).strftime('%d/%m/%y')
            if check_date in meeting:
                if 'Scheduled:' not in meeting:
                    print(f"Warning: The following meeting entry is not formatted correctly: {meeting.strip()}")
                    continue
                description_part, time_date_part = meeting.split('Scheduled:')
                description = description_part.strip('- ').strip()
                time, date = time_date_part.strip().split()
                print(f"- {description} on {date} at {time}")







def load_user_settings():
    """Load user settings from file."""
    global user_settings
    with open(os.path.expanduser("~/.jafr/user-settings.json"), "r") as f:
        user_settings = json.load(f)

def change_master_directory():
    """Change Jafr's master directory."""
    new_directory = input("Which directory would you like Jafr to use?\n")
    user_settings['master'] = new_directory
    with open(os.path.expanduser("~/.jafr/user-settings.json"), "w") as f:
        json.dump(user_settings, f)
    print(f"Master directory changed to {new_directory}.")



# Assuming you want to load the settings when the script starts
load_user_settings()





def mark_tasks_as_completed(tasks, master_dir):
    """Mark selected tasks as completed."""
    # Display incomplete tasks with a number
    incomplete_tasks = [(index, task) for index, task in enumerate(tasks) if "not complete" in task]
    
    if not incomplete_tasks:
        print("No tasks to complete!")
        return

    print("Which task(s) would you like to mark as completed?")
    counter = 1
    task_mapping = {}
    for original_index, task in incomplete_tasks:
        if 'Due:' in task:
            try:
                description, due_date = task.split('Due:')
                due_date = due_date.split()[0]
                print(f"{counter}. {description.strip('- ').strip()} by {due_date}")
                task_mapping[counter] = original_index
                counter += 1
            except ValueError:
                pass

    # Get user input and validate
    while True:
        try:
            task_nums = list(map(int, input().split()))
            for num in task_nums:
                if num < 1 or num >= counter:
                    raise ValueError
            break
        except ValueError:
            print("Please enter valid task numbers.")

    # Mark selected tasks as complete
    for num in task_nums:
        original_index = task_mapping[num]
        tasks[original_index] = tasks[original_index].replace("not complete", "complete")

    # Save the updated tasks back to the file
    with open(os.path.join(master_dir, "tasks.md"), "w") as f:
        f.writelines(tasks)

    print("Marked as complete.")








def add_new_meeting(meetings, master_dir, current_user_id, current_user_name, user_settings_file):
    """Add a new meeting."""
    
    # Prompt for meeting description and re-prompt if empty or contains only whitespace
    description = input("Please enter a meeting description:\n")
    while not description.strip():
        print("Meeting description cannot be empty.")
        description = input("")

    
    # Define regex patterns for date and time
    date_pattern = r'^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/\d{2}$'
    time_pattern = r'^\d{2}:\d{2}$'  # matches format HH:MM

    scheduled_date = input("Please enter a date:\n")
    while not re.match(date_pattern, scheduled_date):
        print("Invalid input. Please try again.")
        
        scheduled_date = input("")

    scheduled_time = input("Please enter a time:\n")
    while not re.match(time_pattern, scheduled_time):
        print("Invalid input. Please try again.")
        
        scheduled_time = input("")

    
    # Format the meeting string as per the expected format
    formatted_meeting = f"\n##### added by you\n- {description} Scheduled: {scheduled_time} {scheduled_date}\n"
    
    meetings.append(formatted_meeting)
    
    # Save the updated meetings back to the file
    with open(os.path.join(master_dir, "meetings.md"), "w") as f:
        f.writelines(meetings)

    print(f"Ok, I have added {description} on {scheduled_date} at {scheduled_time}.")
    
    share_decision = input("Would you like to share this meeting? [y/n]: ")
    
    if share_decision.lower() == 'y':
        share_meeting(meetings, current_user_id, current_user_name, user_settings_file, len(meetings))






def share_task(tasks, current_user_id, current_user_name, user_settings_file):
    # 1. Display all tasks for the user to select which one to share
    print("Which task would you like to share?")
    for i, task in enumerate(tasks, 1):
        task_details = task.split(' Due: ')
        if len(task_details) < 2:  # Check if the task has the expected format
            continue
        task_name = task_details[0].strip().replace('-', '').strip()
        due_date = task_details[1].split(' ')[0]
        print(f"{i}. {task_name} by {due_date}")
    
    while True:
        # 2. Get the selected task based on its number
        try:
            task_num = int(input())
            if 1 <= task_num <= len(tasks):  # Check if the number is within the range of the list
                selected_task = tasks[task_num - 1]
                break  # Break out of the loop if the input is valid
            else:
                print("Invalid input. Please try again.")
        except ValueError:  # If user does not input a number
            print("Invalid input. Please try again.")

    


    # 3. Load users from the passwd file
    users = load_users_from_passwd()

    # Display all user IDs and user names except for the current user
    print("Who would you like to share with?")
    valid_user_ids = []  # list to hold valid user IDs
    for user in users:
        if user['user_id'] != current_user_id:
            print(f"{user['user_id']} {user['username']}")
            valid_user_ids.append(user['user_id'])

    # Get the user IDs of the users to share with
    while True:
        share_ids = input().split()
        
        # Check if all entered IDs are valid
        if all(share_id in valid_user_ids for share_id in share_ids):
            break
        else:
            print("Invalid input. Please try again.")


    # 5. Append the selected task to the appropriate tasks.md file of the selected users
    for shared_user_id in share_ids:
        # Fetch the home directory of the shared user from the password file
        user_home_dir = next(user['home_dir'] for user in users if user['user_id'] == shared_user_id) #/home/jessica
        
        # Formulate the path for their user-settings.json
        shared_user_settings_path = os.path.join(user_home_dir, ".jafr", "user-settings.json")
        

        # Check if the user-settings.json exists for the shared user
        if not os.path.exists(shared_user_settings_path):
            print(f"Warning: user-settings.json does not exist for User {shared_user_id}. Skipping...")
            continue

        # Load their settings
        with open(shared_user_settings_path, 'r') as f:
            shared_user_settings = json.load(f)
            

        # Check if the user has the 'master_dir' attribute in their settings
        master_dir = shared_user_settings.get('master', "")
        
        # master_dir = shared_user_settings.get('master_dir')
        if not master_dir:
            print(f"Warning: User {shared_user_id} does not have a valid 'master_dir' in their settings. Skipping...")
            continue

        # Get their master directory and build the path to their tasks.md
        target_file_path = os.path.join(master_dir, "tasks.md")

        # Write the shared task to their tasks.md
        with open(target_file_path, 'a') as f:
            f.write(f"\n##### shared by {current_user_name}\n{selected_task.strip()}\n")
    
    # 6. Display the confirmation message
    print("Task shared.")



def load_users_from_passwd():
    file_path = sys.argv[1]
    """Parse the passwd file and return a list of user details."""
    users = []
    with open(file_path, 'r') as f:
        for line in f.readlines():
            if not line.strip():  # skip empty lines
                continue
            
            username, _, user_id, _, _, home_dir, _ = line.strip().split(':')
            user = {
                'username': username,
                'user_id': user_id,
                'home_dir': home_dir
            }
            users.append(user)
    return users








def share_meeting(meetings, current_user_id, current_user_name, user_settings_file, latest_meeting_index=None):
    # Load the current user's settings
    with open(user_settings_file, 'r') as f:
        user_settings = json.load(f)

    # Display all meetings for the user to select which one to share
    formatted_meetings = []
    for meeting in meetings:
        parts = meeting.strip().split(" Scheduled: ")
        if len(parts) < 2:
            continue  # Skip this iteration if the expected format is not found
        name = parts[0].replace("-", "").strip()

        time_date_parts = parts[1].split()
        if len(time_date_parts) == 2:
            time, date = time_date_parts
        else:
            print(f"Unexpected format for meeting: {meeting}. Skipping...")
            continue

        formatted_meetings.append(f"{name} on {date} at {time}")

    if not latest_meeting_index:
        print("Which meeting would you like to share?")
        for i, formatted_meeting in enumerate(formatted_meetings, 1):
            print(f"{i}. {formatted_meeting}")

    while True:
        # Get the selected meeting based on its number
        try:
            meeting_num = int(input()) if latest_meeting_index is None else latest_meeting_index
            if 1 <= meeting_num <= len(meetings):
                selected_meeting = meetings[meeting_num - 1]
                break
            else:
                print("Invalid input. Please try again.")
        except ValueError:
            print("Invalid input. Please try again.")

    if "##### added by you" in selected_meeting:
        selected_meeting = selected_meeting.replace("##### added by you\n", "")



    # Load users from the passwd file
    users = load_users_from_passwd()


    # Display all user IDs and user names except for the current user
    print("Who would you like to share with?")
    valid_user_ids = []  # list to hold valid user IDs
    for user in users:
        if user['user_id'] != current_user_id:
            print(f"{user['user_id']} {user['username']}")
            valid_user_ids.append(user['user_id'])

    # Get the user IDs of the users to share with
    while True:
        share_ids = input().split()
        
        # Check if all entered IDs are valid
        if all(share_id in valid_user_ids for share_id in share_ids):
            break
        else:
            print("Invalid input. Please try again.")


    # Append the selected meeting to the appropriate meetings.md file of the selected users
    for shared_user_id in share_ids:
        # Fetch the home directory of the shared user from the password file
        user_home_dir = next(user['home_dir'] for user in users if user['user_id'] == shared_user_id)
        
        # Formulate the path for their user-settings.json
        shared_user_settings_path = os.path.join(user_home_dir, ".jafr", "user-settings.json")
        
        # Load their settings
        with open(shared_user_settings_path, 'r') as f:
            shared_user_settings = json.load(f)

        # Get the master directory of the shared user
        master_dir = shared_user_settings.get('master', "")
        if not master_dir:
            print(f"Warning: User {shared_user_id} does not have a valid 'master_dir' in their settings. Skipping...")
            continue

        # Formulate the path to their meetings.md
        target_file_path = os.path.join(master_dir, "meetings.md")
        
        # Write the shared meeting to their meetings.md with the appropriate prefix
        with open(target_file_path, 'a') as f:
            f.write(f"\n##### shared by {current_user_name}\n{selected_meeting.strip()}\n")

    # Display the confirmation message
    print("Meeting shared.")

















def main():
    # Read user settings
    user_settings_file = os.path.expanduser("~/.jafr/user-settings.json")
    with open(user_settings_file, "r") as f:
        user_settings = json.load(f)
        

    master_dir = user_settings.get('master', "")
    
    
    # Check if the master directory exists
    if not os.path.exists(master_dir):
        print("Jafr's chosen master directory does not exist.", file=sys.stderr)
        return  # Exit the function

    # Check if both tasks.md and meetings.md are present
    tasks_path = os.path.join(master_dir, "tasks.md")
    meetings_path = os.path.join(master_dir, "meetings.md")
    
    if not os.path.exists(tasks_path) or not os.path.exists(meetings_path):
        print("Missing tasks.md or meetings.md file.", file=sys.stderr)
        return  # Exit the function if any of the files is missing

    # Read tasks and meetings
    with open(tasks_path, "r") as f:
        tasks = f.readlines()

    with open(meetings_path, "r") as f:
        meetings = f.readlines()
        

    # Display tasks and meetings
    display_reminders(tasks, meetings)

    # Load all users
    users = load_users_from_passwd()

    # Get current user details (assuming current user's ID matches some logic, here just an example)
    current_username = os.getenv('USER') or os.getenv('USERNAME')

    current_user = next(user for user in users if user['username'] == current_username)
 
    
    # Main menu loop
    while True:

        # Display menu options
        display_user_menu()
        
        choice = input("")

        if choice == "1":
            mark_tasks_as_completed(tasks, master_dir)
        elif choice == "2":
            add_new_meeting(meetings, master_dir, current_user['user_id'], current_user['username'], user_settings_file)
        elif choice == "3":
            share_task(tasks, current_user['user_id'], current_user['username'], user_settings_file)
        elif choice == "4":
            share_meeting(meetings, current_user['user_id'], current_user['username'], user_settings_file)
        elif choice == "5":
            change_master_directory()
        elif choice == "6":
            break
        else:
            print("Invalid choice. Please try again.")
            break

        

if __name__ == '__main__':
    main()


