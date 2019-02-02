from lxml import etree

users_file_name = 'Users.xml'
votes_file_name = 'Votes.xml'

max_user_id = 10000000
max_vote_id = 179182874

def users_data_extractor(users):
    print('>> Start processing Users to get their info ...')

    found_users = 0

    for event, row in etree.iterparse(users_file_name, events=('start', 'end')):
        if event == 'end':
            if not row.get('Id'):
                row.clear()
                row.getparent().remove(row) 
                continue
            
            # first, get the id
            id = int(row.get('Id'))

            # for better performance
            if id > max_user_id:
                break
            
            # if id % 10000 == 0:
            #     print(id)
            
            if id in users:
                users[id]['id'] = id
                users[id]['DisplayName'] = row.get('DisplayName')
                users[id]['Reputation'] = row.get('Reputation')
                found_users += 1
            
            row.clear()
            row.getparent().remove(row)

    return users

def fill_votes_of_answer(answer, dataset_row):
    vote_type = int(dataset_row.get('VoteTypeId'))
    if vote_type == 1:
        answer['best_answer'] = True
    if vote_type == 2:
        answer['positive_vote'] += 1
    if vote_type == 3:
        answer['negative_vote'] += 1
    
    return answer

def votes_data_extractor(answers):
    print('>> Start processing Votes to get + and - votes of answers ...')

    for event, row in etree.iterparse(votes_file_name, events=('start', 'end')):
        if event == 'end':
            # first, get the id and post id
            id = row.get('Id')
            if not id:
                try:
                    row.clear()
                    row.getparent().remove(row)
                except:
                    print('# got an error in reading votes id: ', id)
                continue
            
            id = int(id)
            post_id = int(row.get('PostId'))

            # for better performance
            if id > max_vote_id:
                break

            if id % 100000 == 0:
                print(id)
            
            if post_id in answers:
                answers[post_id] = fill_votes_of_answer(answers[post_id], row)
            
            try:
                row.clear()
                row.getparent().remove(row)
            except:
                print('# got an error in reading votes id: ', id)
    
    print('>> ...Processing Votes finished')
    
    return answers