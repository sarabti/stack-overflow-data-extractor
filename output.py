import html
from collections import defaultdict
import re

train_output_file_name = 'train.txt'
train_errors_file_name = 'train_errors.txt'
test_output_file_name = 'test.txt'
test_errors_file_name = 'test_errors.txt'
users_10_directory_name = './users10'
users_15_directory_name = './users15'
users_20_directory_name = './users20'
users_info_file_name = 'users_info.txt'

def fine_format(line):
    # return html.escape(line).replace('\n', '&#10;').replace('\r', '&#13;').replace('\t', ' ')
    return re.sub('<.*?>', ' ', line).replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')

def group_answers_for_questions(answers):
    grouped_answers = defaultdict(list)

    for answer in answers.values():
        grouped_answers[answer['qid']].append(answer)

    return grouped_answers

def create_users_output(users, train_questions):
    count_of_10_users = 0
    count_of_15_users = 0
    count_of_20_users = 0

    for user_id in users:
        user_content = users[user_id]['DisplayName'] + '\t' + str(users[user_id]['Reputation']) + '\n'

        answers_count = 0
        for answer in users[user_id]['answers']:
            try:
                question = train_questions[int(answer['qid'])]
            except:
                print('! not found question for answer id ', answer['aid'])
                continue
            
            if 'Title' not in question:
                continue
            user_content += question['Title'] + '\t'
            user_content += fine_format(question['Body']) + '\t'
            if 'Body' not in answer:
                continue
            user_content += fine_format(answer['Body']) + '\t'
            user_content += str(answer['best_answer']) + '\t'
            user_content += str(answer['positive_vote']) + '\t'
            user_content += str(answer['negative_vote']) + '\n'
            answers_count += 1
        
        if answers_count >= 10:
            count_of_10_users += 1
            with open(users_10_directory_name + '/' + str(user_id), 'w', encoding='utf-8') as user_file:
                user_file.write(user_content + '\n')
        
        if answers_count >= 15:
            count_of_15_users += 1
            with open(users_15_directory_name + '/' + str(user_id), 'w', encoding='utf-8') as user_file:
                user_file.write(user_content + '\n')
        
        if answers_count >= 20:
            count_of_20_users += 1
            with open(users_20_directory_name + '/' + str(user_id), 'w', encoding='utf-8') as user_file:
                user_file.write(user_content + '\n')
    
    with open(users_info_file_name, 'w', encoding='utf-8') as info_file:
        info_file.write('<====================== USERS ======================>' + '\n')
        info_file.write('> number of users with more than 10 questions: '+ str(count_of_10_users) + '\n')
        info_file.write('> number of users with more than 15 questions: '+ str(count_of_15_users) + '\n')
        info_file.write('> number of users with more than 20 questions: '+ str(count_of_20_users) + '\n')

        
def create_question_session_output(questions, answers, type):
    if type == 'TRAIN':
        file_name = train_output_file_name
    else:
        file_name = test_output_file_name
    
    questions_with_missed_answers = 0
    questions_without_best_answer = 0
    skipped_questions = []

    with open(file_name, 'w', encoding='utf-8') as question_file:
        for question_id in questions:
            if 'Title' not in questions[question_id]:
                continue
            line = str(questions[question_id]['asker']) + '\t'
            line += str(question_id) + '\t'
            line += questions[question_id]['Title'] + '\t'
            line += fine_format(questions[question_id]['Body']) + '\t'
        
            answers_count = 0
            best_answerer_found = False

            for answer in answers[question_id]:
                if answer['best_answer']:
                    best_answerer_found = True
                answers_count += 1
                line += str(answer['answerer']) + '\t'
                line += str(answer['best_answer']) + '\t'
                line += str(answer['positive_vote']) + '\t'
                line += str(answer['negative_vote']) + '\t'
            
            if best_answerer_found:
                question_file.write(line + '\n')
            else:
                questions_without_best_answer  += 1
                skipped_questions.append(question_id)

            initialAnswersCount = questions[question_id]['AnswerCount']

            if initialAnswersCount != answers_count:
                questions_with_missed_answers += 1
    
    return questions_with_missed_answers, questions_without_best_answer, skipped_questions

def create_errors_output(initial_questions, found_questions, missed_answer_questions, without_best_answer_questions, skipped_questions, type):
    if type == 'TRAIN':
        error_file_name = train_errors_file_name
    else:
        error_file_name = test_errors_file_name
    
    with open(error_file_name, 'w', encoding='utf-8') as error_file:
        error_file.write('<====================== '+ type + ' QUESTIONS ======================>' + '\n')
        error_file.write('> number of initial ' + type + ' questions: '+ str(initial_questions) + '\n')
        error_file.write('> number of found questions: ' + str(found_questions) + '\n')
        error_file.write('> ' +  str(initial_questions - found_questions) + ' questions NOT FOUND' + '\n')
        error_file.write('> number of questions with missed answers: ' + str(missed_answer_questions) + '\n')
        error_file.write('> ' + str(without_best_answer_questions) + ' questions were without best answers so they were SKIPPED !' + '\n')
        error_file.write('> list of their ids: ' + '\n')
        error_file.write(str(skipped_questions) + '\n')

