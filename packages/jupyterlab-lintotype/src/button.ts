import { IDisposable, DisposableDelegate } from '@phosphor/disposable';

import { ToolbarButton } from '@jupyterlab/apputils';

import { DocumentRegistry } from '@jupyterlab/docregistry';

import { NotebookPanel, INotebookModel } from '@jupyterlab/notebook';

import { ILintotypeManager } from '.';

export class LintotypeButton
  implements DocumentRegistry.IWidgetExtension<NotebookPanel, INotebookModel> {
  manager: ILintotypeManager;

  createNew(
    panel: NotebookPanel,
    context: DocumentRegistry.IContext<INotebookModel>
  ): IDisposable {
    let button = new ToolbarButton({
      iconClassName: 'jp-LintotypeIcon jp-Icon jp-Icon-16',
      onClick: () => this.manager.lintifyNotebook(panel),
      tooltip: 'Code Overlays'
    });

    panel.toolbar.insertItem(9, 'lintotype', button);

    return new DisposableDelegate(() => button.dispose());
  }
}
