# -*- coding: utf-8 -*-
import scrapy

from scrapy.spiders import Rule
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from newspaper import Article
import pandas as pd
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from selenium import webdriver
from sumy.parsers.html import HtmlParser
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
#from sumy.summarizers.lsa import LsaSummarizer as Summarizer
#from sumy.summarizers.lex_rank import LexRankSummarizer as Summarizer
from sumy.summarizers.text_rank import TextRankSummarizer as Summarizer
#from sumy.summarizers.luhn import LuhnSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
import nltk
import polyglot


class NewsSpider(scrapy.Spider):
    name = "news"
    allowed_domains = ["http://www.eluniversal.com.mx"]

    start_urls = (
        'http://www.eluniversal.com.mx/minuto-x-minuto',
    )

    rules = (Rule(LxmlLinkExtractor(

        restrict_xpaths=(".//*[@id='block-system-main']//span//a")),

    follow=False, callback='parse_item'),)

    #response.xpath('//span//a/text()').extract()[2:-1]

    def parse(self, response):
        driver = webdriver.PhantomJS()
        driver.get('http://www.eluniversal.com.mx/minuto-x-minuto')
        links = driver.find_elements_by_xpath('''.//*[@id='block-system-main']/div/div/div/div[2]/div/div/div/div/div[2]/div/span/a''')
        links = [x.get_attribute('href') for x in links][2:-1]
        col_of_links = pd.DataFrame(links, columns=['URL'])
        # col_of_links.to_csv('/Users/user/Downloads/el_universal.csv',
        #                     na_rep='NaN', index=False)
        print(col_of_links)


        def text_extractor(link):
            article = Article(link, language='es')
            article.download()
            article.parse()
            text = article.text
            return text

        def summarize(url):
            LANGUAGE = "spanish"
            SENTENCES_COUNT = 3
            parser = HtmlParser.from_url(url, Tokenizer(LANGUAGE))
            # or for plain text files
            # parser = PlaintextParser.from_file("document.txt", Tokenizer(LANGUAGE))
            stemmer = Stemmer(LANGUAGE)
            summarizer = Summarizer(stemmer)
            summarizer.stop_words = get_stop_words(LANGUAGE)
            # summary = []
            summary = summarizer(parser.document, SENTENCES_COUNT)
            # summary = [summary[:-1] for e in [summary]]
            # summary = [int(i[1]) for i in summary]
            return summary

        #url = "http://www.eluniversal.com.mx/articulo/nacion/seguridad/2016/12/21/soldados-aseguran-nueve-en-casa-de-seguridad-en-zihuatanejo"
        #summarize(url)

        col_of_links['content'] = col_of_links['URL'].apply(text_extractor)
        #col_of_links['summ'] = col_of_links['content'].apply(summarize)

        df = col_of_links.replace({r'\n\n': ' '}, regex=True)

        ################################################
        #Sentence segmentation:

        df['sents'] = df['content'].apply(lambda x: nltk.sent_tokenize(x.strip(' ')))
        s = df.apply(lambda x: pd.Series(x['sents']), axis=1).stack().reset_index(level=1, drop=True)
        s.name = 'sents'
        df = df.drop(['sents', 'content'], axis=1).join(s)
        df.to_csv('/Users/user/Desktop/sentences_ElUniversal.csv', index=False, sep='|')
        df.reset_index(drop=True, inplace=True)
        #df

        ################################################
        #Relation extraction (Who?):
        # etiquetamos

        from polyglot.text import Text
        from collections import OrderedDict

        #POS-tagging with polyglot
        def postag(doc):
            # especificar que idioma usar?
            text = Text(str(doc), hint_language_code='pt')
            # text.detect_language()
            tags = text.pos_tags
            #vals = {'sutent': 'PF_MOLECULE', 'afinitor': 'PF_MOLECULE', 'votrient': 'PF_MOLECULE'}
            #lis = [(a, vals[a.lower()]) if a.lower() in vals else (a, b) for a, b in tags]
            return tags
            # return ", ".join( repr(e) for e in lis )

        # print(tags)

        df['tags'] = df['sents'].apply(postag)








        df.to_csv('/Users/user/Downloads/el_universal.csv', na_rep='NaN', index=False, sep='|')



