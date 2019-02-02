def make_sessions(sessions_file_name):
    session_file_handler = open(sessions_file_name, 'r')

    sessions = {}
    
    while True:
        line = session_file_handler.readline()
        if not line:
            break
        fields = line.split(',')
        session_entry = {}
        session_entry['answerer'] = []
        for field in fields:
            key_value_pair = field.split(':')
            key = str(key_value_pair[0])
            value = int(key_value_pair[1])
            if key =='answerer':
                session_entry['answerer'].append(value)
            else:
                session_entry[key] = value
        
        sessions[session_entry['qid']] = session_entry
    
    session_file_handler.close()
    session_qids = list(sessions.keys())
    session_length = len(session_qids)

    return sessions, session_qids, session_length 