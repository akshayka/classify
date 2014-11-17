import argparse
from classifier_factory import make_classifier
from data_cleaner_factory import make_data_cleaner
import pickle
from tabulate import tabulate


def tabulate_f1_summary(cv_results_tr, cv_results_tst, labels):
    headers = ['Label', 'Train: F1', 'Test: F1']
    avgs = []
    for label in labels:
        avgs = avgs + [[0, 0]]
    fold = 1
    for f_tr, f_tst in zip(cv_results_tr[2], cv_results_tst[2]):
        for i in range(len(labels)):
            avgs[i][0] = avgs[i][0] + f_tr[i]
            avgs[i][1] = avgs[i][1] + f_tst[i]
        fold = fold + 1
    avgs = [[avg[0] / (fold - 1), avg[1] / (fold - 1)] for avg in avgs]
    for i, label in enumerate(labels):
        avgs[i] = [label] + avgs[i]
    print tabulate(avgs, headers, tablefmt='grid')


def tabulate_results(cv_results, average, labels):
    header = ['fold']
    for label in labels:
        label_str = str(label)
        header.append(label_str + ': precision')
        header.append(label_str + ': recall')
        header.append(label_str + ': f1')
    results = []
    avgs = [0] * len(labels) * 3
    fold = 1
    for p, r, f in zip(cv_results[0], cv_results[1], cv_results[2]):
        entry = [str(fold)]
        for i in range(len(labels)):
            entry = entry + [p[i], r[i], f[i]]
        if not average:
            results.append(entry)
        for i in range(len(avgs) / 3):
            a_i = i * 3
            avgs[a_i] = avgs[a_i] + p[i]
            avgs[a_i+1] = avgs[a_i+1] + r[i]
            avgs[a_i+2] = avgs[a_i+2] + f[i]
        fold = fold + 1
    avgs = [avg / (fold - 1) for avg in avgs]
    avgs = ['avg'] + avgs
    results.append(avgs)
    print tabulate(results, header, tablefmt='grid')


def invoke_classifier(classifier, data_filename,
                      average, train_test_only, data_cleaner):
    results = []
    labels = data_cleaner.labels()
    with open(data_filename, 'rb') as infile:
        # Slice off headers
        # TODO: Headers aren't getting used anywhere,
        # perhaps don't take them in ingest_dataset
        dataset = pickle.load(infile)[1:]
        dataset =  data_cleaner.process_records(dataset)
        cv_results_train, cv_results_test = classifier.cross_validate(dataset)

    dcname = data_cleaner.name
    print 'Classification results for file %s ...;\nusing classifier %s and ' \
          'data_cleaner %s' % (data_filename, classifier.name, dcname)
    if train_test_only:
        tabulate_f1_summary(cv_results_train, cv_results_test, labels)
    else:
        print 'Results: Making predictions on the training set.'
        tabulate_results(cv_results_train, average, labels)
        print 'Results: Making predictions on the test set.'
        tabulate_results(cv_results_test, average, labels)


def main():
    parser = argparse.ArgumentParser(description='applies a classifier to '
                                     'train, test folds generated using '
                                     'ingest_datasets.py')
    parser.add_argument('data_file', type=str, help='ingested data file')
    parser.add_argument('-avg', '--average', action='store_true',
                        help='only output the average of the metrics computed '
                        'during cross validation.')
    parser.add_argument('-tr_tst', '--train_test_f1', action='store_true',
                        help='print a consolidated table of labels versus '
                        'training and test error, as measured by f1 scores.')
    parser.add_argument('data_cleaner', type=str,
                        help='apply a DataCleaner to the data ingested by '
                        'ingest_datasets.py; see data_cleaner_factory.py for '
                        'a list of supported cleaners')
    parser.add_argument('-b', '--binary', action='store_true',
                        help='use binary labels')
    parser.add_argument('-n', '--collapse_numbers', action='store_true',
                        help='collapse all numbers to single token')
    parser.add_argument('-np', '--noun_phrases', action='store_true',
                        help='engineer features from noun phrases')
    parser.add_argument('-fs', '--first_sentence', type=int, default=1,
                        help='upweight first sentence')
    parser.add_argument('classifier', type=str,
                        help='apply a particular classifier to the data; see '
                        'classifier_factory.py for a list of supported '
                        'classifiers')
    parser.add_argument('-rf', '--reduce_features', action='store_true',
                        help='run RFECV to reduce features (backwards search)')
    parser.add_argument('-kb', '--k_best', type=int, default=0,
                        help='k best features to use (chi2 elimination)')
    parser.add_argument('-t', '--token_pattern_idx', type=int,
                        default=0,
                        help='index corresponding to token_pattern in '
                        'CUSTOM_TOKEN_PATTERNS -- see custom_token_patterns.py')
    parser.add_argument('-tf', '--tfidf', action='store_true',
                        help='include to use tfidf')
    parser.add_argument('-c', '--custom_stop_words', action='store_true',
                        help='include to use the custom stop word list')
    parser.add_argument('-p', '--penalty', type=float, default=1.0,
                        help='penalty (C term) for linear svm')
    args = parser.parse_args()

    classifier = make_classifier(args.classifier, args.reduce_features,
                                 args.k_best,
                                 args.token_pattern_idx,
                                 args.tfidf, args.custom_stop_words,
                                 args.penalty)
    data_cleaner = make_data_cleaner(dc=args.data_cleaner,
                                     binary=args.binary,
                                     collapse_numbers=args.collapse_numbers,
                                     extract_noun_phrases=args.noun_phrases,
                                     first_sentence_weight=args.first_sentence)
    invoke_classifier(classifier, args.data_file, args.average,
                      args.train_test_f1, data_cleaner)


if __name__ == '__main__':
    main()
