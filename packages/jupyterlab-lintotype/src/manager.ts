import { PromiseDelegate } from '@phosphor/coreutils';

import { NotebookPanel } from '@jupyterlab/notebook';
import { Cell } from '@jupyterlab/cells';

import { KernelMessage, Kernel } from '@jupyterlab/services';

import { NAME, ILintotypeManager } from '.';

export class LintotypeManager implements ILintotypeManager {
  private nextMsgId = 0;
  private promises = new Map<
    number,
    PromiseDelegate<ILintotypeManager.ILintoTypeResponse>
  >();
  linters = new Map<string, ILintotypeManager.ILinter>();

  lintifyNotebook(panel: NotebookPanel) {
    if (this.linters.has(panel.session.kernel.id)) {
      return;
    }

    this.registerCommTarget(panel.session.kernel);
  }

  async annotateNotebook(
    notebook: NotebookPanel,
    cell: Cell
  ): Promise<ILintotypeManager.ILintoTypeResponse> {
    let linter = this.linters.get(notebook.session.kernel.id);
    if (!linter) {
      return;
    }

    let allCode: ILintotypeManager.IInputMimeBundle = {};
    let { cells, metadata } = notebook.model;
    let numCells = cells.length;
    for (let i = 0; i < numCells; i++) {
      let cell = cells.get(i);
      let cellCode = cell.value.text;
      if (!allCode[cell.mimeType]) {
        allCode[cell.mimeType] = [];
      }
      allCode[cell.mimeType].push({
        cell_id: cell.id,
        code: cellCode
      });
    }
    let lintotypeMeta = (metadata.get(NAME) || {}) as object;
    let response: ILintotypeManager.ILintoTypeResponse;
    try {
      response = await linter(cell.model.id, allCode, lintotypeMeta);
    } catch (err) {
      console.warn(err);
    }
    return response;
  }

  registerCommTarget(kernel: Kernel.IKernelConnection) {
    kernel.registerCommTarget(
      NAME,
      async (comm: Kernel.IComm, _msg: KernelMessage.ICommOpenMsg) => {
        this.linters.set(
          kernel.id,
          async (
            cellId: string,
            code: ILintotypeManager.IInputMimeBundle,
            metadata: object
          ) => {
            let requestId = this.nextMsgId++;
            let promise = new PromiseDelegate<
              ILintotypeManager.ILintoTypeResponse
            >();
            this.promises.set(requestId, promise);
            comm.send({
              request_id: requestId,
              cell_id: cellId,
              code,
              metadata: metadata as any
            });
            return await promise.promise;
          }
        );

        comm.onMsg = (msg: KernelMessage.ICommMsgMsg) => {
          let requestId: number = (msg.content.data as any).request_id;
          let { data } = msg.content;
          let response = (data as any) as ILintotypeManager.ILintoTypeResponse;
          this.promises.get(requestId).resolve(response);
        };
      }
    );
  }
}
