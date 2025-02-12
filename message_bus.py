import queue

ranking_queue = queue.Queue()
social_queue = queue.Queue()
insights_queue = queue.Queue()

def send_message(queue_name, message):
    if queue_name == 'topics_generated':
        ranking_queue.put({'queue': queue_name, 'body': message})
        insights_queue.put({'queue': queue_name, 'body': message})
    elif queue_name == 'rankings_created':
        social_queue.put({'queue': queue_name, 'body': message})
        insights_queue.put({'queue': queue_name, 'body': message})
