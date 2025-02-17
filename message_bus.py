import queue

# Creating separate queues for different types of messages
ranking_queue = queue.Queue()
social_queue = queue.Queue()
insights_queue = queue.Queue()

# Function to send messages to the appropriate queues
def send_message(queue_name, message):
    if queue_name == 'topics_generated':
        ranking_queue.put({'queue': queue_name, 'body': message})
        insights_queue.put({'queue': queue_name, 'body': message})
    elif queue_name == 'rankings_created':
        social_queue.put({'queue': queue_name, 'body': message})
        insights_queue.put({'queue': queue_name, 'body': message})
