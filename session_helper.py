def fill_question_fields(session_entry, dataset_row):
    session_entry['Title'] = dataset_row.get('Title')
    session_entry['Body'] = dataset_row.get('Body')

    if dataset_row.get('OwnerUserId'):
        session_entry['asker'] = int(dataset_row.get('OwnerUserId'))
    else:
        session_entry['asker'] = None
    
    if dataset_row.get('AnswerCount'):
        session_entry['AnswerCount'] = min(int(dataset_row.get('AnswerCount')), session_entry['AnswerCount'])
    
    if dataset_row.get('AcceptedAnswerId'):
        session_entry['AcceptedAnswerId'] = int(dataset_row.get('AcceptedAnswerId'))
    else:
        session_entry['AcceptedAnswerId'] = None 
    
    return session_entry

def fill_answer_fields(dataset_row):
    session_entry = {}
    session_entry['aid'] = int(dataset_row.get('Id'))
    session_entry['qid'] = int(dataset_row.get('ParentId'))
    session_entry['answerer'] = int(dataset_row.get('OwnerUserId'))
    session_entry['Body'] = dataset_row.get('Body')

    return session_entry

def make_initial_vote_fields(answers):
    for answer in answers.values():
        answer['positive_vote'] = 0
        answer['negative_vote'] = 0
        answer['best_answer'] = False
    
    return answers

def get_answerers(answers):
    users = {}
    
    for answer in answers.values():
        answerer_id = answer['answerer']

        if not answerer_id:
            continue
        
        if answerer_id not in users:
            users[answerer_id] = {}
            users[answerer_id]['answers'] = []
        
        users[answerer_id]['answers'].append(answer)
    
    return users
