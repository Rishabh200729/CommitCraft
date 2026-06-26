import React from 'react';
import { Button } from './ui/Button';

export function LoginForm() {
  return (
    <form>
      <input type="text" placeholder="Username" />
      <Button variant="primary">Login</Button>
    </form>
  );
}
