import 'codemirror/addon/lint/lint.js';

import { JupyterLab, JupyterLabPlugin } from '@jupyterlab/application';

import { PLUGIN_ID as id, ILintotypeManager } from '.';
import { LintotypeButton } from './button';
import { LintotypeManager } from './manager';

import 'codemirror/addon/lint/lint.css';
import '../style/index.css';

const plugin: JupyterLabPlugin<ILintotypeManager> = {
  id,
  requires: [],
  provides: ILintotypeManager,
  autoStart: true,
  activate: (app: JupyterLab) => {
    let manager = new LintotypeManager();
    let button = new LintotypeButton();
    button.manager = manager;
    app.docRegistry.addWidgetExtension('Notebook', button);
    return manager;
  }
};

export default plugin;
