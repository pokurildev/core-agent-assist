import React from 'react';
import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/ui/button';
import { Settings, ListStart, LogOut } from 'lucide-react';
import { cn } from '@/lib/utils';

const Layout: React.FC = () => {
    const { logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    const navItems = [
        { name: 'Settings', icon: Settings, href: '/' },
        { name: 'Logs', icon: ListStart, href: '/logs' },
    ];

    return (
        <div className="flex h-screen bg-background">
            {/* Sidebar */}
            <aside className="w-64 border-r bg-card flex flex-col">
                <div className="p-6 border-b">
                    <h2 className="text-xl font-bold tracking-tight">Voice Bot Admin</h2>
                </div>
                <nav className="flex-1 p-4 space-y-2">
                    {navItems.map((item) => (
                        <NavLink
                            key={item.name}
                            to={item.href}
                            className={({ isActive }) =>
                                cn(
                                    'flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors',
                                    isActive
                                        ? 'bg-primary text-primary-foreground'
                                        : 'text-muted-foreground hover:bg-muted'
                                )
                            }
                        >
                            <item.icon className="h-4 w-4" />
                            {item.name}
                        </NavLink>
                    ))}
                </nav>
            </aside>

            {/* Main Content */}
            <div className="flex-1 flex flex-col overflow-hidden">
                {/* Topbar */}
                <header className="h-16 border-b bg-card flex items-center justify-between px-8">
                    <div className="text-sm text-muted-foreground italic">
                        Connected to: http://localhost:8000
                    </div>
                    <Button variant="ghost" size="sm" onClick={handleLogout} className="text-muted-foreground h-9">
                        <LogOut className="h-4 w-4 mr-2" />
                        Logout
                    </Button>
                </header>

                {/* Workspace */}
                <main className="flex-1 overflow-y-auto p-8">
                    <Outlet />
                </main>
            </div>
        </div>
    );
};

export default Layout;
