"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import { clearAuthToken, getAuthToken } from "@/lib/auth";
import { ROUTES } from "@/constants/routes";
import { UserBadge } from "@/features/auth/components/UserBadge";

const links = [
  { href: ROUTES.home, label: "Home" },
  { href: ROUTES.products, label: "Products" },
  { href: ROUTES.cart, label: "Cart" },
  { href: ROUTES.checkout, label: "Checkout" },
  { href: ROUTES.transactions, label: "Transactions" },
  { href: ROUTES.dashboard, label: "Dashboard" },
  { href: ROUTES.login, label: "Login" },
  { href: ROUTES.register, label: "Register" },
];
const guestLinks: string[] = [ROUTES.home, ROUTES.login, ROUTES.register];
const hiddenWhenLoggedIn: string[] = [ROUTES.login, ROUTES.register];

export function Header() {
  const pathname = usePathname();
  const router = useRouter();
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    setIsLoggedIn(Boolean(getAuthToken()));
  }, [pathname]);

  const navLinks = useMemo(() => {
    if (!isLoggedIn) return links.filter((link) => guestLinks.includes(link.href));
    return links.filter((link) => !hiddenWhenLoggedIn.includes(link.href));
  }, [isLoggedIn]);

  const logout = () => {
    clearAuthToken();
    setIsLoggedIn(false);
    router.push(ROUTES.login);
  };

  return (
    <header className="sticky top-0 z-20 border-b border-slate-200/70 surface">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
        <div>
          <Link href={ROUTES.home} className="text-xl font-extrabold tracking-tight text-ink">
            Migro<span className="text-coral">Shop</span>
          </Link>
          <UserBadge />
        </div>
        <nav className="flex flex-wrap items-center gap-2">
          {navLinks.map((link) => {
            const active = pathname === link.href;
            return (
              <Link
                key={link.href}
                href={link.href}
                className={`rounded-full px-3 py-1.5 text-sm font-medium transition ${active ? "bg-ink text-white" : "text-slate-600 hover:bg-slate-100"}`}
              >
                {link.label}
              </Link>
            );
          })}
          {isLoggedIn ? (
            <button onClick={logout} type="button" className="rounded-full bg-coral px-3 py-1.5 text-sm font-semibold text-white hover:opacity-90">
              Logout
            </button>
          ) : null}
        </nav>
      </div>
    </header>
  );
}
