import { Handle, Position, NodeProps } from '@xyflow/react';
import { FileCode2 } from 'lucide-react';
import clsx from 'clsx';

export function FileNode({ data, type }: NodeProps) {
  // Map backend graph types to visual states
  const styles = {
    modified: 'border-accent-blue bg-surface-card',
    added: 'border-accent-green bg-surface-card',
    removed: 'border-accent-red bg-surface-card opacity-50 border-dashed',
    impacted: 'border-accent-yellow bg-surface-card',
    dependency: 'border-hairline bg-surface',
  };

  // If node type doesn't match our specific types, default to dependency style
  const styleClass = styles[type as keyof typeof styles] || styles.dependency;

  return (
    <div 
      className={clsx("px-4 py-3 rounded-lg border flex items-center gap-3 w-[250px] cursor-pointer", styleClass)}
      onClick={data.onClick as any}
    >
      <Handle type="target" position={Position.Top} className="w-2 h-2 !bg-mute border-none" />
      <div className="shrink-0 p-2 rounded-md bg-surface border border-hairline-soft">
        <FileCode2 className="w-4 h-4 text-mute" />
      </div>
      <div className="flex flex-col min-w-0 overflow-hidden">
        <span className="text-body-md font-medium text-ink truncate block" title={data.label as string}>
          {data.label as string}
        </span>
        <div className="flex items-center gap-2 mt-1">
          <span className="text-caption-sm text-mute uppercase tracking-wider">
            {type === 'modified' ? 'Target' : type}
          </span>
          {(data.owners as string[])?.length > 0 && (
            <span className="bg-accent-blue-soft text-accent-blue text-[10px] px-1.5 py-0.5 rounded-[4px] whitespace-nowrap">
              {(data.owners as string[])[0]}
            </span>
          )}
          {(data.flows as string[])?.length > 0 && (
            <span className="bg-surface-elevated text-ink border border-hairline text-[10px] px-1.5 py-0.5 rounded-[4px] whitespace-nowrap">
              {(data.flows as string[])[0]} Flow
            </span>
          )}
        </div>
      </div>
      <Handle type="source" position={Position.Bottom} className="w-2 h-2 !bg-mute border-none" />
    </div>
  );
}
