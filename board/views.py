from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Question
from django.utils.dateparse import parse_date
import random
# Create your views here.

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
        return render(request, 'board/category_sort.html', {'header': header, 'matches': results})
    except:
        return render(request, 'board/category_sort.html', {'header': header, 'matches': None})

def gameboard(request):
    questions = [None] * 25
    header = "Categories:"
    for i in range(0, 5):
        question = get_object_or_404(Question, pk=random.randint(0, Question.objects.count()))
        cat = question.category
        header += " " + cat + ","
        matches = Question.objects.filter(category__iexact = cat)[:5]
        for j, match in enumerate(matches):
            questions[i + j*5] = match
    header = header[:-1]
    return render(request, 'board/category_sort.html', {'header': header, 'matches': questions})

def random_question(request):
    question = get_object_or_404(Question, pk=random.randint(0, Question.objects.count()))
    return render(request, 'board/detail.html', {'question': question})

def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'board/detail.html', {'question': question})