"""
A Python script to redact name entities on comments on a fictional site. The script reads a CSV (with at least one
column named 'text'), invokes Stanford NER classifier to detect Name Entities on the values of the text, redacts all
tokens tagged as 'PERSON' from the input, and writes the output to a new CSV file with the same content as the input
except for the 'text' column which is replaced by 'redacted_text'.

As Stanford NER is a java library, Jython is required to run this script. Here's an example run:

java -Dpython.path=stanford-ner-2014-01-04/stanford-ner.jar -jar jython-standalone-2.7-b2.jar redact_name_entities.py comments_df.csv comments_df_redacted.csv

This assumes that the Stanford NER was decompressed on the same folder as the script.
"""

# Python modules

from csv import DictReader, DictWriter, QUOTE_ALL
from os.path import exists
from sys import exit

# Java libraries

from edu.stanford.nlp.ie.crf import CRFClassifier
from edu.stanford.nlp.ling.CoreAnnotations import AnswerAnnotation


def main(args):
    if not exists(args.input):
        print 'Unable to found input CSV file "{0}".'.format(args.input)
        exit(1)

    if exists(args.output) and not args.overwrite:
        print 'Output file "{0}" already exists and no overwrite option was supplied.'.format(args.output)
        exit(1)

    print 'Redacting name entities on comments. input_file = "{0}", output_file="{1}"...'.format(
        args.input, args.output
    )

    with open(args.input, 'rb') as input_file, open(args.output, 'wb') as output_file:
        dict_reader = DictReader(input_file)

        dict_writer = DictWriter(
            output_file,
            fieldnames=('id', 'email', 'first_name', 'last_name', 'place', 'obfuscated_text', 'timestamp'),
            quoting=QUOTE_ALL
        )
        dict_writer.writeheader()

        classifier = CRFClassifier.getClassifierNoExceptions(
            'stanford-ner-2014-01-04/classifiers/english.all.3class.distsim.crf.ser.gz'
        )

        for row in dict_reader:
            redacted_text = row['text']
            classify_result = classifier.classify(row['text']);

            for sentence in classify_result:
                for word in sentence:
                    token = word.originalText()
                    tag = word.get(AnswerAnnotation)

                    if tag == 'PERSON':
                        redacted_text = redacted_text.replace(token, '****')

            row['redacted_text'] = redacted_text
            del row['text']

            dict_writer.writerow(row)

    print 'Done.'

if __name__ == '__main__':
    import argparse

    argument_parser = argparse.ArgumentParser(description='Redacts name entities on comments text.')
    argument_parser.add_argument('input', help='input CSV file')
    argument_parser.add_argument('output', help='output CSV file')
    argument_parser.add_argument(
        '--overwrite', action='store_true',
        help='whether to overwrite and existing output file (Default: false)', default=False
    )

    main(argument_parser.parse_args())
