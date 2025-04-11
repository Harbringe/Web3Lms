"use client";

import { useState } from 'react';
import axios from '@/utils/axios';

interface PaymentFormProps {
  orderId: string;
  amount: number;
}

export default function PaymentForm({ orderId, amount }: PaymentFormProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handlePayment = async () => {
    try {
      setIsLoading(true);
      setError('');

      // Get Razorpay order details
      const response = await axios.post(`payment/razorpay-checkout/${orderId}/`);
      const { order_id, amount, currency, key } = response.data;

      // Initialize Razorpay
      const options = {
        key,
        amount,
        currency,
        name: 'Your Company Name',
        description: 'Course Purchase',
        order_id,
        handler: async (response: any) => {
          try {
            // Verify payment
            const { data } = await axios.post('payment/payment-success/', {
              order_oid: orderId,
              razorpay_payment_id: response.razorpay_payment_id,
              razorpay_order_id: response.razorpay_order_id,
              razorpay_signature: response.razorpay_signature
            });

            // Handle success
            window.location.href = `/payment-success/${orderId}`;
          } catch (error) {
            setError('Payment verification failed');
          }
        },
        prefill: {
          name: 'User Name',
          email: 'user@example.com',
        },
        theme: {
          color: '#4F46E5'
        }
      };

      const razorpay = new (window as any).Razorpay(options);
      razorpay.open();
    } catch (error) {
      setError('Failed to initialize payment');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="mt-6">
      {error && (
        <div className="text-red-500 text-sm mb-4">{error}</div>
      )}
      <button
        onClick={handlePayment}
        disabled={isLoading}
        className="w-full bg-indigo-600 text-white py-3 rounded-lg hover:bg-indigo-700 disabled:opacity-50"
      >
        {isLoading ? 'Processing...' : 'Pay Now'}
      </button>
    </div>
  );
} 