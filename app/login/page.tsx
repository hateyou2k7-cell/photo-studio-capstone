'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import { useAuthStore } from '@/store/useAuthStore';

const loginSchema = z.object({
  email: z.string().email('Email không hợp lệ'),
  password: z.string().min(6, 'Mật khẩu tối thiểu 6 ký tự'),
});

type LoginForm = z.infer<typeof loginSchema>;

export default function LoginPage() {
  const router = useRouter();
  const setAuth = useAuthStore((state) => state.setAuth);

  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginForm) => {
    try {
      const res = await api.post('/auth/login', data);
      if (res.data.user.role !== 'PROVIDER') {
        alert('Tài khoản không phải Provider!');
        return;
      }
      setAuth(res.data.user, res.data.accessToken);
      router.push('/provider/rooms');
    } catch (err: any) {
      alert(err.response?.data?.message || 'Đăng nhập thất bại!');
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-100">
      <form onSubmit={handleSubmit(onSubmit)} className="w-full max-w-md bg-white p-8 rounded-lg shadow-md space-y-4">
        <h2 className="text-2xl font-bold text-center">Đăng nhập Provider</h2>
        <div>
          <label className="block text-sm font-medium">Email</label>
          <input {...register('email')} className="w-full p-2 border rounded mt-1" type="email" />
          {errors.email && <p className="text-red-500 text-sm mt-1">{errors.email.message}</p>}
        </div>
        <div>
          <label className="block text-sm font-medium">Mật khẩu</label>
          <input {...register('password')} className="w-full p-2 border rounded mt-1" type="password" />
          {errors.password && <p className="text-red-500 text-sm mt-1">{errors.password.message}</p>}
        </div>
        <button type="submit" disabled={isSubmitting} className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 disabled:bg-gray-400">
          {isSubmitting ? 'Đang xử lý...' : 'Đăng nhập'}
        </button>
      </form>
    </div>
  );
}