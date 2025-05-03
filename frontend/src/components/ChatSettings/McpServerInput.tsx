// components/widgets/McpServerInput.tsx

import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { IInput } from 'types/Input'
import { InputStateHandler } from './InputStateHandler'
import { useState } from 'react';

interface McpServerInputProps
  extends IInput,
    Omit<React.InputHTMLAttributes<any>, 'id' | 'size'> {
  setField?: (field: string, value: string[], shouldValidate?: boolean) => void
  values?: {
    host?: string
    mcpPath?: string
    authPath?: string
    userId?: string
    password?: string
  }
}

const McpServerInput = ({
  id,
  label,
  tooltip,
  description,
  hasError,
  disabled,
  setField,
  values = {},
}: McpServerInputProps): JSX.Element => {
  const [localValues, setLocalValues] = useState(values);

  const handleChange = (field: keyof typeof values, value: string) => {
    const updatedValues = { ...localValues, [field]: value };
    setLocalValues(updatedValues); // ローカル状態を更新

    // values全体をstring[]形式に変換してsetFieldを呼び出す
    const updatedArray = [
      updatedValues.host ?? "",
      updatedValues.mcpPath ?? "",
      updatedValues.authPath ?? "",
      updatedValues.userId ?? "",
      updatedValues.password ?? ""
    ];
    setField?.(id, updatedArray, false); // 親コンポーネントに通知
  };

  return (
    <InputStateHandler
      id={id}
      label={label}
      tooltip={tooltip}
      description={description}
      hasError={hasError}
    >
      <div className="space-y-2">
        <div>
          <Label htmlFor={`${id}-host`}>ホスト（含ポート）</Label>
          <Input
            id={`${id}-host`}
            value={localValues.host ?? ''}
            onChange={(e) => handleChange('host', e.target.value)}
            disabled={disabled}
          />
        </div>
        <div>
          <Label htmlFor={`${id}-mcpPath`}>MCP endpoint (URI)</Label>
          <Input
            id={`${id}-mcpPath`}
            value={localValues.mcpPath ?? ''}
            onChange={(e) => handleChange('mcpPath', e.target.value)}
            disabled={disabled}
          />
        </div>
        <div>
          <Label htmlFor={`${id}-authPath`}>認証URI</Label>
          <Input
            id={`${id}-authPath`}
            value={localValues.authPath ?? ''}
            onChange={(e) => handleChange('authPath', e.target.value)}
            disabled={disabled}
          />
        </div>
        <div>
          <Label htmlFor={`${id}-userId`}>ユーザID</Label>
          <Input
            id={`${id}-userId`}
            value={localValues.userId ?? ''}
            onChange={(e) => handleChange('userId', e.target.value)}
            disabled={disabled}
          />
        </div>
        <div>
          <Label htmlFor={`${id}-password`}>パスワード</Label>
          <Input
            id={`${id}-password`}
            type="password"
            value={localValues.password ?? ''}
            onChange={(e) => handleChange('password', e.target.value)}
            disabled={disabled}
          />
        </div>
      </div>
    </InputStateHandler>
  );
};

export { McpServerInput }
export type { McpServerInputProps }
