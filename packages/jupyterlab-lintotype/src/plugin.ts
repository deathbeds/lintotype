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

    const markdownContext = new Widget();
    markdownContext.id = `id-lintotype-context-${nextId++}`;
    markdownContext.title.closable = true;

    manager.contextRequested.connect(
      async (_: any, context: ILintotypeManager.IMarkupContext) => {
        const { value, kind } = context.content;
        markdownContext.title.label = context.title;
        switch (kind) {
          default:
            return;
          case 'markdown':
            await renderMarkdown({
              host: markdownContext.node,
              source: value,
              trusted: true,
              sanitizer,
              shouldTypeset: false,
              latexTypesetter: null,
              resolver: null,
              linkHandler: null
            });
            break;
        }
        _app.shell.addToMainArea(markdownContext, { mode: 'split-right' });
      }
    );

    return manager;
  }
};

export default plugin;
