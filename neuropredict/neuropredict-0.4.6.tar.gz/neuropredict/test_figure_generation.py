import rhst
import visualize

import numpy as np

data_loc = '/Users/Reddy/opensource/neuropredict/test_MLdatasets/paths.txt'
out_dir  = '/Users/Reddy/opensource/neuropredict/test_ppmi'

# rhst.run(data_loc, out_dir, num_repetitions=20)

num_cl = 2
num_rep=200
num_ds = 4
metric = np.random.rand(num_rep,num_ds)
labels = ['c1', 'c2', 'c3']

cm = np.round(np.random.rand(num_cl,num_cl, num_rep, num_ds)*100)
cm_labels = [ 'a', 'b', 'c' ]
method_names = ['method']*num_ds
# visualize.confusion_matrix_per_feature(cm, labels, method_names, out_dir+'/posthoc_confmat')

results_file_path = '/Users/Reddy/opensource/neuropredict/test_ppmi/rhst_results.pkl'
dataset_paths, train_perc, num_repetitions, num_classes, \
pred_prob_per_class, pred_labels_per_rep_fs, test_labels_per_rep, \
best_min_leaf_size, best_num_predictors, \
feature_importances_rf, feature_names, \
num_times_misclfd, num_times_tested, \
confusion_matrix, class_order, class_sizes, accuracy_balanced, auc_weighted, positive_class = \
    rhst.load_results(results_file_path)

# visualize.freq_hist_misclassifications(num_times_misclfd, num_times_tested, method_names,
#                                        out_dir + '/vis_freq_hist',
#                                        separate_plots=False)

# visualize.metric_distribution(accuracy_balanced, method_names, out_dir + '/posthoc_metric_vis')

# visualize.compare_misclf_pairwise(confusion_matrix, class_order, method_names, out_dir+'/posthoc_radar')

visualize.feature_importance_map(feature_importances_rf, method_names,
                                 out_dir+'/featimp',
                                 feature_names=feature_names,
                                 show_distr=False)