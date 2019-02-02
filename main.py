import numpy as np
from lxml import etree
import time

from input import make_sessions
from session_helper import  fill_question_fields,\
                            fill_answer_fields, \
                            make_initial_vote_fields, \
                            get_answerers
from data_extractors import users_data_extractor, votes_data_extractor
from output import  group_answers_for_questions, \
                    create_users_output, \
                    create_question_session_output, \
                    create_errors_output

train_sessions_file_name = 'sessions.trn'
test_sessions_file_name = 'sessions.tst'

posts_file_name = 'Posts.xml'

### Obtained by querying stackoverflow real data (for better performance and ignoring unwanted rows)
# max_post_id = 4572699
max_post_id = 2529401

if __name__ == '__main__':
    train_sessions, train_qid_sessions, initial_train_sessions_length = make_sessions(train_sessions_file_name)
    found_train_questions = 0

    test_sessions, test_qid_sessions, initial_test_sessions_length = make_sessions(test_sessions_file_name)
    found_test_questions = 0

    answers = {}

    print('>> Start processing Posts to get train and test questions and answers ...')

    ### start timer ...
    start_timer = time.time()

    for event, row in etree.iterparse(posts_file_name, events=('start', 'end')):
        if event == 'end':
            # first, get the id and parent id
            id = int(row.get('Id'))
            parent_id = None if not row.get('ParentId') else int(row.get('ParentId'))

            # for better performance
            if id > max_post_id:
                break

            found = False
            
            if id in train_sessions:
                found = True
                train_sessions[id] = fill_question_fields(train_sessions[id], row)
                if train_sessions[id]['asker'] and train_sessions[id]['Title'] and train_sessions[id]['Body']:
                    found_train_questions += 1
                    train_qid_sessions.remove(id)
                else:
                    del train_sessions[id]
            
            if id in test_sessions:
                found = True
                test_sessions[id] = fill_question_fields(test_sessions[id], row)
                if test_sessions[id]['asker'] and test_sessions[id]['Title'] and test_sessions[id]['Body']:
                    found_test_questions += 1
                    test_qid_sessions.remove(id)
                else:
                    del test_sessions[id]
            
            if found:
                row.clear()
                row.getparent().remove(row) 
                continue

            if parent_id and (parent_id in train_sessions or parent_id in test_sessions):
                if row.get('OwnerUserId'):
                    answers[id] = fill_answer_fields(row)
            
            row.clear()
            row.getparent().remove(row) 

    print('>> ...Processing Posts finished')

    ### Initial Votes Data
    answers = make_initial_vote_fields(answers)

    ### Extract Votes Data
    answers = votes_data_extractor(answers)

    ### Extract Needed Users From Answers
    users = get_answerers(answers)
    
    ### Extract Users Data
    users = users_data_extractor(users)

    ### end timer ...
    end_timer = time.time()
    print('>>> The execution took ', end_timer - start_timer,' seconds')

    '''
    ' Output part
    '
    '''
    grouped_answers = group_answers_for_questions(answers)

    create_users_output(users, train_sessions)

    missed_answer_trains, without_best_answer_trains, skipped_trains = create_question_session_output(train_sessions, grouped_answers, 'TRAIN')

    create_errors_output(initial_train_sessions_length, found_train_questions, missed_answer_trains, without_best_answer_trains, skipped_trains, 'TRAIN')

    missed_answer_tests, without_best_answer_tests, skipped_tests = create_question_session_output(test_sessions, grouped_answers, 'TEST')

    create_errors_output(initial_test_sessions_length, found_test_questions, missed_answer_tests, without_best_answer_tests, skipped_tests, 'TEST')
