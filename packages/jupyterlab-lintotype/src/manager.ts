import CodeMirror from 'codemirror';

import { PromiseDelegate } from '@phosphor/coreutils';

import { NotebookPanel } from '@jupyterlab/notebook';

import { KernelMessage, Kernel } from '@jupyterlab/services';

import { NAME, ILintotypeManager } from '.';

export class LintotypeManager implements ILintotypeManager {
  private nextId = 0;
  private promises = new Map<
    number,
    PromiseDelegate<LintotypeManager.IAnnotation[]>
  >();
  private linters = new Map<string, LintotypeManager.ILinter>();

  lintifyNotebook(panel: NotebookPanel) {
    panel.model.contentChanged.connect(() => {
      for (const widget of panel.content.widgets) {
        const cm = (widget.editor as any)._editor as CodeMirror.Editor;
        if (!cm.getOption('lint')) {
          const { gutters, lint } = this.cmSettings(panel);
          cm.setOption('gutters', gutters);
          cm.setOption('lint', lint);
        }
      }
    });
    this.registerCommTarget(panel.session.kernel);
    // TODO: allow config in settings, notebook
    // const metaUpdated = (metadata: IObservableJSON) => {
    //   console.log('metadata', metadata);
    // };
    //
    // panel.model.metadata.changed.connect(metaUpdated);
    // metaUpdated(panel.model.metadata);
  }

  cmSettings(panel: NotebookPanel) {
    return {
      gutters: ['CodeMirror-lint-markers'],
      lint: {
        async: true,
        hasGutter: true,
        getAnnotations: async (
          code: string,
          callback: (annotations: any[]) => void
        ): Promise<void> => {
          const anno = await this.linters.get(panel.session.kernel.id)(code);
          callback(
            anno.map(pos => {
              return {
                ...pos,
                from: new CodeMirror.Pos(pos.from.line, pos.from.col),
                to: new CodeMirror.Pos(pos.to.line, pos.to.col)
              };
            })
          );
        }
      }
    };
  }

  registerCommTarget(kernel: Kernel.IKernelConnection) {
    kernel.registerCommTarget(
      NAME,
      async (comm: Kernel.IComm, msg: KernelMessage.ICommOpenMsg) => {
        this.linters.set(kernel.id, async (code: string) => {
          let id = this.nextId++;
          let promise = new PromiseDelegate<LintotypeManager.IAnnotation[]>();
          this.promises.set(id, promise);
          comm.send({ code, id });
          return await promise.promise;
        });

        comm.onMsg = (msg: KernelMessage.ICommMsgMsg) => {
          let id: number = (msg.content.data as any).id;
          this.promises.get(id).resolve((msg.content.data as any).annotations);
        };
      }
    );
  }
}

export namespace LintotypeManager {
  export interface IPos {
    line: number;
    col: number;
  }

  export interface IAnnotation {
    message: string;
    severity: string;
    from: IPos;
    to: IPos;
  }

  export interface ILinter {
    (code: string): Promise<IAnnotation[]>;
  }
}
