import { NotebookPanel } from '@jupyterlab/notebook';
import { Cell } from '@jupyterlab/cells';
import CodeMirror from 'codemirror';
import { Diagnostic } from 'vscode-languageserver-types';
import { ILintotypeManager } from '..';

const CM_SEVERITY = {
  1: 'error',
  2: 'warning',
  3: 'information',
  4: 'hint'
};

export class CodeMirrorAnnotator
  implements ILintotypeManager.IAnnotationRenderer {
  private _lintotype: ILintotypeManager;

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
        delay: 50,
        getAnnotations: async (
          _code: string,
          callback: (annotations: CodeMirrorAnnotator.IMark[]) => void
        ): Promise<void> => {
          let { diagnostics } = await this._lintotype.annotateNotebook(
            panel,
            cell
          );

          try {
            callback(
              diagnostics[cell.model.mimeType].map(diag => this.lspToCM(diag))
            );
          } catch {
            callback([]);
          }
        }
      }
    };
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
