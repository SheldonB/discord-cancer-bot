import logging

import markovify

from cancerbot import datastore

log = logging.getLogger(__name__)

class CustomMarkovText(markovify.Text):

    def _prepare_text(self, text):
        text = text.strip()

        if not text.endswith(('.', '?', '!')):
            text += '.'

        return text

    def sentence_split(self, text):
        text = self._prepare_text(text)

        return markovify.split_into_sentences(text)

class MarkovManager:

    ALL_KEY = '__ALL__'

    def __init__(self, server_context):
        self.server_context = server_context

        self.cache_chain = {}

    def make_sentence_server(self):
        log.debug('Generating Markov Sentence based off entire server text')

        if self.ALL_KEY not in self.cache_chain:
            log.debug('Markov Chain for server %s not found in cache. Generating it.', self.server_context.server.name)

            messages = datastore.get_messages_by_server(self.server_context.server)

            content = [message['content'] for message in messages]

            chain = CustomMarkovText(content)

            self.cache_chain[self.ALL_KEY] = chain

        return self.cache_chain[self.ALL_KEY].make_sentence(tries=150)


    def make_sentence_user(self, user):
        log.debug('Generating Markov Sentence for user %s', user)

        if user not in self.cache_chain:
            log.debug('Markov Chain for user %s from server %s not found in cache. Generating it.', user, self.server_context.server.name)

            messages = datastore.get_messages_by_username(user)

            content = [message['content'] for message in messages]

            if len(content) == 0:
                return None

            chain = CustomMarkovText(content)

            self.cache_chain[user] = chain

        return self.cache_chain[user].make_sentence(tries=150)
