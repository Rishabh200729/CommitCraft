import { Handle, Position, NodeProps } from '@xyflow/react';
import { FileCode2 } from 'lucide-react';
import clsx from 'clsx';

export function FileNode({ data, type }: NodeProps) {
  // Map backend graph types to visual states
  const styles = {
    modified: 'border-accent-blue bg-surface-card',
    impacted: 'border-accent-yellow bg-surface-card',
    dependency: 'border-hairline bg-surface',
  };

  // If node type doesn't match our specific types, default to dependency style
  const styleClass = styles[type as keyof typeof styles] || styles.dependency;

  return (
    <div className={clsx("px-4 py-3 rounded-lg border flex items-center gap-3 w-[250px]", styleClass)}>
      <Handle type="target" position={Position.Top} className="w-2 h-2 !bg-mute border-none" />
      <div className="shrink-0 p-2 rounded-md bg-surface border border-hairline-soft">
        <FileCode2 className="w-4 h-4 text-mute" />
      </div>
      <div className="flex flex-col min-w-0 overflow-hidden">
        <span className="text-body-md font-medium text-ink truncate block" title={data.label as string}>
          {data.label as string}
        </span>
        <span className="text-caption-sm text-mute uppercase tracking-wider">
          {type === 'modified' ? 'Target' : type}
        </span>
      </div>
      <Handle type="source" position={Position.Bottom} className="w-2 h-2 !bg-mute border-none" />
    </div>
  );
}
