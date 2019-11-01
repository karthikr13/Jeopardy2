from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Question
from django.utils.dateparse import parse_date
import random, requests, json
# Create your views here.

class Question2():
    def __init__(self, question_text, score, ask_date, category, answer_text):
        self.question_text = question_text
        self.score = str(score)
        self.ask_date = ask_date.split('T')[0]
        self.category = category
        self.answer_text = answer_text
    def __str__(self):
        return self.question_text + " " + self.score + " " + self.ask_date + " " + self.category + " " + self.answer_text
def index(request):
    return render(request, 'board/index.html')

def search(request, search_string):
    split_search = search_string.split('&')
    terms = [None, None, None, None]
    for i, term in enumerate(split_search):
        terms[i] = term.split('=')[1]
        if not terms[i]:
            terms[i] = 'All'
    matches = Question.objects.all()
    header = ''
    if terms[0] != 'All':
        matches = matches.filter(category__iexact = terms[0])
        header += terms[0].title()
    else:
        header += 'All questions'
    if terms[1] != 'All':
        matches = matches.filter(score__exact = terms[1])
        header += ' for ' + terms[1]
    else:
        header += ' for any points'
    if terms[2] != 'All':
        header += ', asked after ' + terms[2]
        terms[2] = parse_date(terms[2])
        matches = matches.filter(ask_date__gte = terms[2])
        asked = True
    else:
        asked = False
    if terms[3] != 'All':
        if asked:
            header += ' and before ' + terms[3]
        else:
            header += ', asked before' + terms[3]
        terms[3] = parse_date(terms[3])
        matches = matches.filter(ask_date__lte = terms[3])

    paginator = Paginator(matches, 25)
    try:
        page = request.GET.get('page')
        results = paginator.get_page(page)
        row1 = results[0:5]
        row2 = results[5:10]
        row3 = results[10:15]
        row4 = results[15:20]
        row5 = results[20:25]
        return render(request, 'board/category_sort.html', {'header': header, 'matches': results, 'row1': row1, 'row2': row2, 'row3': row3, 'row4': row4, 'row5':row5})
    except:
        return render(request, 'board/category_sort.html', {'header': header, 'matches': None})
def sort_rows(x):
    if not x:
        return 10000
    return int(x.score)
'''
clean(col): method to ensure scores displayed in gameboard are unique and consistent across columns
sometimes, questions collected may be of same value, leading to scores in a column such as [100, 100, 200, 300, 400]
sometimes, daily double rounds get combined with regular rounds, so some columns are multiples of 200 while others are multiples of 100
col: column to clean
returns cleaned column
'''
def clean(col):
    i = 1
    for question in col:
        if not question:
            break
        question.score = i * 100
        i += 1
    return col
def gameboard(request):
    questions = [None] * 25
    header = "Categories:"
    cats = []
    categories = {}
    with open('categories.json') as json_file:
        categories = json.load(json_file)
    for i in range(0, 5):
        question = None
        cat = None
        generated = None
        while not cat:
            index = random.randint(0, len(categories))
            cat = list(categories.keys())[index]
            cat_id = categories[cat]
            url = 'http://jservice.io/api/category?id='+str(cat_id)
            r  = requests.get(url)
            generated = r.json()
            if generated['clues_count'] < 5:
                cat = None
                continue
            cats.append(cat)
        matches = [None]*5
        j = 0
        for question in generated['clues']:
            q_text = question['question']
            a_text = question['answer']
            score = question['value']
            airdate = question['airdate']
            category = cat
            if None in [q_text, a_text, score, airdate, category] or score == 0:
                continue
            q = Question2(q_text, score, airdate, category, a_text)
            if j >= len(matches):
                break
            matches[j] = q
            j += 1
        for j, match in enumerate(matches):
            questions[i*5+j] = match
        '''
        while not question:
            try:
                question = Question.objects.filter(pk__exact = random.randint(0, Question.objects.count()))[0]
            except:
                question = None
        cat = question.category
        cats.append(cat)
        header += " " + cat + ","
        matches = Question.objects.filter(category__iexact = cat)[:5]
        
        for j, match in enumerate(matches):
            questions[i*5+j] = match
        '''
    header = header[:-1]
    col1 = (sorted(questions[0:5], key = lambda x: sort_rows(x)))
    col2 = (sorted(questions[5:10], key = lambda x: sort_rows(x)))
    col3 = (sorted(questions[10:15], key = lambda x: sort_rows(x)))
    col4 = (sorted(questions[15:20], key = lambda x: sort_rows(x)))
    col5 = (sorted(questions[20:25], key = lambda x: sort_rows(x)))
    
    row1 = [col1[0], col2[0], col3[0], col4[0], col5[0]]
    row2 = [col1[1], col2[1], col3[1], col4[1], col5[1]]
    row3 = [col1[2], col2[2], col3[2], col4[2], col5[2]]
    row4 = [col1[3], col2[3], col3[3], col4[3], col5[3]]
    row5 = [col1[4], col2[4], col3[4], col4[4], col5[4]]
    return render(request, 'board/gameboard.html', {'header': header, 'cats': cats, 'row1': row1, 'row2': row2, 'row3': row3, 'row4': row4, 'row5': row5})

def random_question(request):
    question = None
    url = 'http://jservice.io/api/random'
    r  = requests.get(url)
    generated = r.json()[0]
    while not question:
        
        q_text = generated['question']
        a_text = generated['answer']
        score = generated['value']
        airdate = generated['airdate']
        category = generated['category']['title']
        if None in [q_text, a_text, score, airdate, category] or score == 0:
            url = 'http://jservice.io/api/random'
            r  = requests.get(url)
            generated = r.json()[0]
            continue
        question = Question2(q_text, score, airdate, category, a_text)
        '''
        except:
            url = 'http://jservice.io/api/random'
            r  = requests.get(url)
            generated = r.json()[0]
        '''
    '''
    while not question:
        try:
            question = Question.objects.filter(pk__exact = random.randint(0, Question.objects.count()))[0]
        except:
            question = None
    '''
    return render(request, 'board/random.html', {'question': question})
    print(question)
def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'board/detail.html', {'question': question})