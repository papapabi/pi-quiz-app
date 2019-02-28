# TODO: add score and ASCII arcade start screen
# TODO: look up module and package organization
# TODO: look up if basename imports like these first ones chuck everything
import os
import random
import re

from contextlib import ExitStack
from enum import Enum
from itertools import zip_longest
from pick import pick


class Question(object):
    # TODO: look up how to document attribute information
    # TODO: make attributes self-documenting
    # TODO: where to force expectation, caller or handler
    def __init__(self, question, choices, answer, difficulty, chosen=None):
        self.question = question
        self.choices = choices
        self.answer = answer
        self.difficulty = difficulty
        self.chosen = chosen
    
    def __repr__(self):
        return "{cls}({question}, {chosen}, {answer})".format(
                                cls=self.__class__.__name__,
                                question=self.question,
                                answer=self.answer,
                                chosen=self.chosen)
    
    def prompt(self):
        return f'{self.question} [{self.difficulty.name}]'
    

class Difficulty(Enum):
    EASY = 1
    MEDIUM = 2
    HARD = 3

CATEGORIES = {'Mathematics':'math', 'Science':'science', 
              'Philippine History':'phil'}

def choose_category():
    main_prompt = 'Please choose your desired quiz category:'
    categories = list(CATEGORIES.keys())
    chosen = _pick(prompt=main_prompt, options=categories)
    return CATEGORIES[chosen]

def start_quiz():
    """Returns a list of questions and the user's responses."""
    category = choose_category()
    questions = generate_questions(category)
    for question in questions:
        chosen = _pick(prompt=question.prompt(), options=question.choices)
        question.chosen = chosen
    return questions

def grade_quiz(answered_questions):
    """Returns the score given a list of answered Question objects."""
    return sum(1 * question.difficulty.value 
               for question in answered_questions 
               if question.answer == question.chosen)

def generate_questions(category):
    """Returns a randomized list of Question objects from the given category."""
    # given the path
    # we want to return a list of randomized Question objects
    questions = []
    category_dir = os.path.abspath(category)
    # automate searching for difficulty
    filenames = [f for f in os.listdir(category_dir) if f.endswith('_easy.txt')]
    with ExitStack() as stack:
        files = [stack.enter_context(open(os.path.join(category_dir, fname)))
                 for fname in filenames]
        for answer, choices, question in zip_longest(*files):
            choices = choices.strip().split(" ")
            answer = answer.strip()
            questions.append(Question(question=question,
                                      choices=choices,
                                      answer=answer,
                                      difficulty=Difficulty.EASY))
    random.shuffle(questions)
    return questions

def _pick(prompt, options, indicator='=>'):
    # TODO: look up proper method documentation
    # TODO: look up what happens when you do this parameter->argument naming confusion
    """
    
    A modified interface for pick.pick.
    Side effect: displays to the console with a curses-based interactive selection list.

    Parameters:
    option : a list of options
    """
    option, _ = pick(options=options, title=prompt, indicator=indicator)
    return option


if __name__ == "__main__":
    answered_questions = start_quiz()
    score = grade_quiz(answered_questions)
    print(f"score: {score}")