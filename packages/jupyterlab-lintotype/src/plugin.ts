import 'codemirror/addon/lint/lint.js';

import { JupyterLab, JupyterLabPlugin } from '@jupyterlab/application';
import { INotebookTracker } from '@jupyterlab/notebook';

import { PLUGIN_ID as id, ILintotypeManager } from '.';
import { LintotypeManager } from './manager';

import 'codemirror/addon/lint/lint.css';
import '../style/index.css';

const plugin: JupyterLabPlugin<ILintotypeManager> = {
  id,
  requires: [INotebookTracker],
  provides: ILintotypeManager,
  autoStart: true,
  activate: (app: JupyterLab, notebooks: INotebookTracker) => {
    let manager = new LintotypeManager();

    notebooks.currentChanged.connect(async () => {
      const panel = notebooks.currentWidget;
      await panel.session.ready;
      manager.lintifyNotebook(panel);
    });

    // let button = new LintotypeButton();
    // button.manager = manager;
    // app.docRegistry.addWidgetExtension('Notebook', button);
    return manager;
  }
};

export default plugin;
