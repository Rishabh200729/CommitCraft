import React from 'react';
import { Button } from './ui/Button';

export function PaymentForm() {
  return (
    <form>
      <input type="text" placeholder="Card Number" />
      <Button variant="primary">Submit Payment</Button>
    </form>
  );
}
