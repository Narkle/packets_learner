import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import scikitplot as skplt
import pandas as pd
import numpy as np
import pickle
from sklearn.metrics import f1_score, precision_score, recall_score, accuracy_score, average_precision_score, log_loss
from skopt import BayesSearchCV

from data.data import create_directory

class BaseModel():
    def __init__(self):
        self.model = None
        
    def fit(self, x, y):
        if self.model is not None:
            self.model = self.model.fit(x if isinstance(x, np.ndarray) else x.values, y)
            if isinstance(self.model, BayesSearchCV):
                LOGGER.info(f"Best model's F1: {self.model.best_score_}")
                LOGGER.info(f"Best model's parameters: {self.model.best_params_}")
                self.model = self.model.best_estimator_
            return
        raise NotImplementedError()
        
    def predict(self, x):
        if self.model is not None:
            return self.model.predict(x.values)
        raise NotImplementedError()
 
    def predict_proba(self, x):
        if self.model is not None:
            return self.model.predict_proba(x.values)
        raise NotImplementedError()
        
    def evaluate(self, x, y_true, output_directory):
        """
        Evaluate Model regarding performance metrics
        and some performance-measuring plots
        """
        y_pred_prob = self.predict_proba(x)
        y_pred = self.predict(x)

        output_directory = output_directory / self.__class__.__name__
        output_directory = create_directory(output_directory)
        
        # Metrics
        metrics = {}
        metrics['model'] = self.__class__.__name__
        metrics['f1'] = f1_score(y_true, y_pred)
        metrics['precision'] = precision_score(y_true, y_pred)
        metrics['recall'] = recall_score(y_true, y_pred)
        metrics['accuracy'] = accuracy_score(y_true, y_pred)
        metrics['average_precision'] = average_precision_score(y_true, y_pred)
        metrics['log_loss'] = log_loss(y_true, y_pred_prob)
        pd.DataFrame([metrics], columns=metrics.keys()).to_csv(output_directory / 'metrics.csv', index=False)
        
        # Plots
        with PdfPages(output_directory / 'plots.pdf', 'w') as pdf:
            skplt.metrics.plot_confusion_matrix(y_true, y_pred)
            pdf.savefig()
            plt.close()
            skplt.metrics.plot_confusion_matrix(y_true, y_pred, normalize=True)
            pdf.savefig()
            plt.close()
            skplt.metrics.plot_precision_recall(y_true, y_pred_prob)
            pdf.savefig()
            plt.close()
            skplt.metrics.plot_roc(y_true, y_pred_prob)
            pdf.savefig()
            plt.close()
            if hasattr(self.model, 'feature_importances_'):
                skplt.estimators.plot_feature_importances(self.model)
                pdf.savefig()
            plt.close()
            skplt.metrics.plot_ks_statistic(y_true, y_pred_prob)
            pdf.savefig()
            plt.close()
            skplt.metrics.plot_calibration_curve(y_true, [y_pred_prob])
            pdf.savefig()
            plt.close()
            skplt.metrics.plot_lift_curve(y_true, y_pred_prob)
            pdf.savefig()
            plt.close()
            skplt.metrics.plot_cumulative_gain(y_true, y_pred_prob)
            pdf.savefig()
            plt.close()
    def pickle_model(self, output_directory):
        if self.model is not None:
            output_directory = output_directory / self.__class__.__name__
            output_directory = create_directory(output_directory)
            pickle.dump(self.model, open(output_directory / 'model.pickle', 'wb'))
        