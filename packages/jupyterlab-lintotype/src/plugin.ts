import 'codemirror/addon/lint/lint.js';

import { JupyterLab, JupyterLabPlugin } from '@jupyterlab/application';
import { INotebookTracker } from '@jupyterlab/notebook';

import { PLUGIN_ID as id, ILintotypeManager } from '.';
import { LintotypeManager } from './manager';
import { CodeMirrorAnnotator } from './annotators/codemirror';
import { Widget } from '@phosphor/widgets';
import { defaultSanitizer as sanitizer } from '@jupyterlab/apputils';

import { renderMarkdown } from '@jupyterlab/rendermime';

import 'codemirror/addon/lint/lint.css';
import '../style/index.css';

const plugin: JupyterLabPlugin<ILintotypeManager> = {
  id,
  requires: [INotebookTracker],
  provides: ILintotypeManager,
  autoStart: true,
  activate: (_app: JupyterLab, notebooks: INotebookTracker) => {
    let nextId: 0;
    let manager = new LintotypeManager();

    let cmAnnotator = new CodeMirrorAnnotator(manager);

    notebooks.currentChanged.connect(async () => {
      const panel = notebooks.currentWidget;
      await panel.session.ready;
      manager.lintifyNotebook(panel);
      cmAnnotator.lintifyNotebook(panel);
    });

    manager.contextRequested.connect(
      async (_: any, context: ILintotypeManager.IMarkupContext) => {
        let w = new Widget();
        const { value, kind } = context.content;
        w.id = `id-lintotype-context-${kind}-${nextId++}`;
        w.title.label = context.title;
        switch (kind) {
          case 'markdown':
            await renderMarkdown({
              host: w.node,
              source: value,
              trusted: true,
              sanitizer,
              shouldTypeset: false,
              latexTypesetter: null,
              resolver: null,
              linkHandler: null
            });
            break;
          default:
            break;
        }
        _app.shell.addToMainArea(w);
      }
    );

    // let button = new LintotypeButton();
    // button.manager = manager;
    // app.docRegistry.addWidgetExtension('Notebook', button);
    return manager;
  }
};

export default plugin;
