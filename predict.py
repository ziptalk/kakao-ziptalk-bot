import os
import sys
import json
import logging
import data_helper
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.contrib import learn

from googletrans import Translator

logging.getLogger().setLevel(logging.INFO)

def predict_unseen_data():
	"""Step 0: load trained model and parameters"""
	params = json.loads(open('./parameters.json').read())
	checkpoint_dir = './trained_model_1619689266/'
	if not checkpoint_dir.endswith('/'):
		checkpoint_dir += '/'
	checkpoint_file = tf.train.latest_checkpoint('./trained_model_1619689266/'+ 'checkpoints')
	logging.critical('Loaded the trained model: {}'.format(checkpoint_file))

	"""Step 1: load data for prediction"""
	test_file = './data/small_samples_property.json'
	test_examples = json.loads(open(test_file).read())

	# translator = Translator()
	translator = Translator(service_urls=['translate.googleapis.com'])
	# translator.translate("Der Himmel ist blau und ich mag Bananen", dest='en')

	kor_category = str(test_examples[0]['category'])
	# print(type(kor_category))
	# print(kor_category)
	kor_question = test_examples[0]['question']

	eng_category = translator.translate(kor_category, dest='en')
	eng_question = translator.translate(kor_question, dest='en')
	# print(eng_category.text)

	test_examples[0]['category'] = eng_category.text
	test_examples[0]['question'] = eng_question.text
	# test_examples = test_examples.text

	# labels.json was saved during training, and it has to be loaded during prediction
	labels = json.loads(open('./labels.json').read())
	one_hot = np.zeros((len(labels), len(labels)), int)
	np.fill_diagonal(one_hot, 1)
	label_dict = dict(zip(labels, one_hot))

	x_raw = [example['question'] for example in test_examples]
	x_test = [data_helper.clean_str(x) for x in x_raw]
	logging.info('The number of x_test: {}'.format(len(x_test)))

	y_test = None
	if 'category' in test_examples[0]:
		y_raw = [example['category'] for example in test_examples]
		y_test = [label_dict[y] for y in y_raw]
		logging.info('The number of y_test: {}'.format(len(y_test)))

	vocab_path = os.path.join(checkpoint_dir, "vocab.pickle")
	vocab_processor = learn.preprocessing.VocabularyProcessor.restore(vocab_path)
	x_test = np.array(list(vocab_processor.transform(x_test)))

	"""Step 2: compute the predictions"""
	graph = tf.Graph()
	with graph.as_default():
		session_conf = tf.ConfigProto(allow_soft_placement=True, log_device_placement=False)
		sess = tf.Session(config=session_conf)

		with sess.as_default():
			saver = tf.train.import_meta_graph("{}.meta".format(checkpoint_file))
			saver.restore(sess, checkpoint_file)

			input_x = graph.get_operation_by_name("input_x").outputs[0]
			dropout_keep_prob = graph.get_operation_by_name("dropout_keep_prob").outputs[0]
			predictions = graph.get_operation_by_name("output/predictions").outputs[0]

			batches = data_helper.batch_iter(list(x_test), params['batch_size'], 1, shuffle=False)
			all_predictions = []
			for x_test_batch in batches:
				batch_predictions = sess.run(predictions, {input_x: x_test_batch, dropout_keep_prob: 1.0})
				all_predictions = np.concatenate([all_predictions, batch_predictions])

	if y_test is not None:
		y_test = np.argmax(y_test, axis=1)
		correct_predictions = sum(all_predictions == y_test)

		# Save the actual labels back to file
		actual_labels = [labels[int(prediction)] for prediction in all_predictions]

		for idx, example in enumerate(test_examples):
			example['new_category'] = actual_labels[idx]
		
		with open('./data/small_samples_prediction.json', 'w') as outfile:
			json.dump(test_examples, outfile, indent=4, ensure_ascii=False)

		logging.critical('The accuracy is: {}'.format(correct_predictions / float(len(y_test))))
		logging.critical('The prediction is complete')

# if __name__ == '__main__':
# 	# python3 predict.py ./trained_model_1478649295/ ./data/small_samples.json
# 	predict_unseen_data()
