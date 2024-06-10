from flask import render_template, request, redirect, url_for, current_app , session
from .forms import SearchForm

import sys
import os

# Get the parent directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)

# Add the parent directory to the Python path
sys.path.append(parent_dir)

from AIQueryTransformer.transfrom_prompt import OpenAIDSL
import os

from AIQueryTransformer.constants import (
    BASE_COMPLETION_MODEL,
    CHATGPT_16K_MODEL,
    CHATGPT_MODEL,
    COMPLETION_MODEL,
    EMBEDDINGS_MODEL,
    DEFAULT_MODEL,
    TOKENS_DELTA,
    MAX_TOKENS
)

openai_dsl = OpenAIDSL(
    completion_model=COMPLETION_MODEL,
    embeddings_model=EMBEDDINGS_MODEL,
    model=CHATGPT_16K_MODEL,
    tokens_delta=TOKENS_DELTA,
)

@current_app.route('/', methods=['GET', 'POST'])
def index():
    form = SearchForm()
    if 'conversation' not in session:
        session['conversation'] = []

    if form.validate_on_submit():
        query = form.query.data
        session['conversation'].append({'role': 'user', 'content': query})

        clarity = openai_dsl.assess_clarity_of_request(query)
        
        if clarity == "unclear":
            extracted_items = openai_dsl.extract_items_from_request(query)
            prediction_items = []
            for item in extracted_items:
                if item['price']:
                    prediction_items.append(f"product name: {item['product']}, price: {item['price']}")
                else:
                    prediction_items.append(f"product name: {item['product']}")
            
            items = ', '.join(prediction_items)
            detailed_prompt = f"I want to buy {items}"
            dsl_query = openai_dsl.chat_gpt(detailed_prompt, openai_dsl.get_mapping('amazon-products-index'))
        else:
            dsl_query = openai_dsl.chat_gpt(query, openai_dsl.get_mapping('amazon-products-index'))
        
        results = openai_dsl.get_products_from_query('amazon-products-index', dsl_query)
        session['conversation'].append({'role': 'assistant', 'content': results})
        return render_template('results.html', results=results)

    return render_template('index.html', form=form, conversation=session['conversation'])

@current_app.route('/clear')
def clear_conversation():
    session.pop('conversation', None)
    return redirect(url_for('index'))
