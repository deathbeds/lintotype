import { NotebookPanel } from '@jupyterlab/notebook';
import { Cell } from '@jupyterlab/cells';
import CodeMirror from 'codemirror';
import { Diagnostic, CodeAction } from 'vscode-languageserver-types';
import { ILintotypeManager } from '..';

const CM_SEVERITY = {
  1: 'error',
  2: 'warning',
  3: 'information',
  4: 'hint'
};

export const CSS = {
  BTN_CODE_ACTION: 'jp-LintoType-CodeAction',
  BTN_MARKUP_CTXT: 'jp-LintoType-MarkupContext'
};

export class CodeMirrorAnnotator
  implements ILintotypeManager.IAnnotationRenderer {
  private _lintotype: ILintotypeManager;
  private _lineWidgets = new Map<string, CodeMirror.LineWidget[]>();

  constructor(lintotype: ILintotypeManager) {
    this._lintotype = lintotype;
  }

  lintifyNotebook(panel: NotebookPanel): void {
    const onContentChanged = () => {
      for (const cell of panel.content.widgets) {
        const cm = (cell.editor as any)._editor as CodeMirror.Editor;
        if (!cm.getOption('lint')) {
          const { gutters, lint } = this.cmSettings(panel, cell);
          cm.setOption('gutters', gutters);
          cm.setOption('lint', lint);
        }
      }
    };

    panel.model.contentChanged.connect(onContentChanged);

    onContentChanged();
  }

  lspToCM(diag: Diagnostic): CodeMirrorAnnotator.IMark {
    let { message, severity, range, source, code } = diag;
    let { start, end } = range;

    let cm = {
      message: `${message} [${source}:${code || '?'}]`,
      severity: CM_SEVERITY[severity],
      from: new CodeMirror.Pos(start.line, start.character),
      to: new CodeMirror.Pos(end.line, end.character)
    };

    return cm;
  }

  cmSettings(panel: NotebookPanel, cell: Cell) {
    return {
      gutters: ['CodeMirror-lint-markers'],
      lint: {
        async: true,
        hasGutter: true,
        getAnnotations: async (
          _code: string,
          callback: (annotations: CodeMirrorAnnotator.IMark[]) => void
        ): Promise<void> => {
          let response = await this._lintotype.annotateNotebook(panel, cell);
          if (!response || !response.annotations) {
            return;
          }
          let annotations = response.annotations[cell.model.mimeType];
          let { diagnostics, code_actions, markup_contexts } = annotations;
          try {
            callback((diagnostics || []).map(this.lspToCM));
          } catch {
            callback([]);
          }

          this.makeLineWidgets(cell, code_actions, markup_contexts);
        }
      }
    };
  }

  removeLineWidgets(cell: Cell) {
    for (const widget of this._lineWidgets.get(cell.model.id) || []) {
      widget.clear();
    }
    this._lineWidgets.delete(cell.model.id);
  }

  makeLineWidgets(
    cell: Cell,
    codeActions: CodeAction[] = [],
    contexts: ILintotypeManager.IMarkupContext[] = []
  ) {
    const cm = (cell.editor as any)._editor as CodeMirror.Editor;
    this.removeLineWidgets(cell);

    let lineWidgets: CodeMirror.LineWidget[] = [];

    (codeActions || []).forEach(action => {
      let changes = action.edit.changes[cell.model.id];
      if (changes && changes.length) {
        let btn = document.createElement('button');
        btn.className = CSS.BTN_CODE_ACTION;
        btn.onclick = () => {
          this.removeLineWidgets(cell);
          cm.setValue(changes[0].newText.trim());
          cm.refresh();
          cm.focus();
        };
        btn.textContent = action.title;
        lineWidgets.push(cm.addLineWidget(changes[0].range.end.line, btn));
      }
    });

    (contexts || []).forEach(context => {
      let btn = document.createElement('button');
      btn.textContent = context.title;
      btn.className = CSS.BTN_MARKUP_CTXT;
      btn.onclick = () => {
        this._lintotype.requestContext(context);
      };
      lineWidgets.push(cm.addLineWidget((context.range as any).end.line, btn));
    });

    this._lineWidgets.set(cell.model.id, lineWidgets);
  }
}

export namespace CodeMirrorAnnotator {
  export interface IMark {
    from: CodeMirror.Position;
    to: CodeMirror.Position;
    message: string;
    severity: string;
  }
}
