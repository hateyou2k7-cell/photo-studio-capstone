import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Dashboard App",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="vi">
      <body className="flex min-h-screen m-0 bg-gray-100">
        {}
        <aside className="w-64 bg-slate-800 text-white p-5 flex flex-col gap-4">
          <h2 className="text-xl font-bold border-b border-gray-600 pb-3">Admin Panel</h2>
          <nav className="flex flex-col gap-2">
            <a href="/" className="hover:bg-slate-700 p-2 rounded transition">Trang chủ</a>
            <a href="/provider" className="hover:bg-slate-700 p-2 rounded transition">Provider</a>
            <a href="/settings" className="hover:bg-slate-700 p-2 rounded transition">Cài đặt</a>
          </nav>
        </aside>

        {}
        <main className="flex-1 p-8">
          {children}
        </main>
      </body>
    </html>
  );
}