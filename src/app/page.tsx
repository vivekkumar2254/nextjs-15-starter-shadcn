import Link from 'next/link';
import type { FC } from 'react';

import { Badge, Card, CardContent, CardHeader, CardTitle, Button } from '@/components/ui';
import {
    Bell,
    Bot,
    Calendar,
    CalendarCheck2,
    CalendarClock,
    CheckCircle2,
    Clock3,
    FileBox,
    Gauge,
    IdCard,
    Monitor,
    Network,
    Settings,
    Sparkles,
    Star,
    Users,
    ShieldCheck,
    BarChart3
} from 'lucide-react';

type Action = {
    title: string;
    gradientClass: string; // prettier aesthetic
    href: string;
    Icon: FC<{ className?: string }>;
};

const actions: Action[] = [
    { title: 'Org - Object Replication', Icon: Monitor, gradientClass: 'from-blue-600 to-indigo-600', href: '#' },
    { title: 'INTEGRTR HR Bot', Icon: Bot, gradientClass: 'from-pink-600 to-rose-600', href: '#' },
    { title: 'Delegate Workflows', Icon: CalendarCheck2, gradientClass: 'from-teal-600 to-emerald-600', href: '#' },
    { title: 'View My Profile', Icon: IdCard, gradientClass: 'from-purple-600 to-fuchsia-600', href: '#' },
    { title: 'View Org Chart', Icon: Network, gradientClass: 'from-zinc-600 to-slate-600', href: '#' },
    { title: 'Team Absences', Icon: CalendarClock, gradientClass: 'from-sky-600 to-blue-600', href: '#' },
    { title: 'My Time Sheet', Icon: Clock3, gradientClass: 'from-rose-600 to-pink-600', href: '#' },
    { title: 'Report Center', Icon: BarChart3, gradientClass: 'from-teal-600 to-cyan-600', href: '#' },
    { title: 'Pending Workflows', Icon: FileBox, gradientClass: 'from-violet-600 to-purple-600', href: '#' },
    { title: 'Reminders', Icon: Bell, gradientClass: 'from-stone-600 to-neutral-600', href: '#' },
    { title: 'Favorites', Icon: Star, gradientClass: 'from-blue-600 to-cyan-600', href: '#' }
];

const StatCard: FC<{ title: string; value: string; trend: string; Icon: FC<{ className?: string }>; }> = ({ title, value, trend, Icon }) => (
    <Card className='overflow-hidden'>
        <CardContent className='flex items-center gap-4 p-4'>
            <div className='rounded-xl bg-primary/10 p-3 text-primary'>
                <Icon className='h-5 w-5' />
            </div>
            <div className='min-w-0'>
                <p className='truncate text-xs text-muted-foreground'>{title}</p>
                <div className='flex items-baseline gap-2'>
                    <p className='text-xl font-semibold'>{value}</p>
                    <Badge variant='secondary' className='text-[10px]'>{trend}</Badge>
                </div>
            </div>
        </CardContent>
    </Card>
);

const Page: FC = () => {
    return (
        <div className='flex flex-col gap-6'>
            {/* Hero banner */}
            <Card className='relative overflow-hidden border-none bg-gradient-to-br from-background to-background/40 shadow-sm ring-1 ring-border'>
                <div className='pointer-events-none absolute inset-0 -z-10 bg-[radial-gradient(ellipse_at_top,rgba(99,102,241,0.25),transparent_60%),radial-gradient(ellipse_at_bottom,rgba(56,189,248,0.2),transparent_60%)]' />
                <CardHeader className='pb-2'>
                    <Badge className='w-fit' variant='secondary'>Dashboard</Badge>
                    <CardTitle className='mt-2 text-2xl'>Welcome back, Admin</CardTitle>
                    <p className='max-w-2xl text-sm text-muted-foreground'>A curated cockpit to manage roles, approvals, and your daily operational shortcuts — designed for speed during the hackathon.</p>
                </CardHeader>
                <CardContent className='flex flex-wrap items-center gap-3 pb-6'>
                    <Button asChild size='sm'>
                        <Link href='#'>
                            <Sparkles className='mr-2 h-4 w-4' />
                            Create workflow
                        </Link>
                    </Button>
                    <Button asChild size='sm' variant='outline'>
                        <Link href='#'>
                            <Settings className='mr-2 h-4 w-4' />
                            Preferences
                        </Link>
                    </Button>
                    <div className='ml-auto flex gap-3'>
                        <StatCard title='Active Users' value='1,248' trend='+8.2%' Icon={Users} />
                        <StatCard title='Policy Pass' value='97.3%' trend='+1.1%' Icon={ShieldCheck} />
                        <StatCard title='On‑time Tasks' value='92%' trend='+3.4%' Icon={CheckCircle2} />
                    </div>
                </CardContent>
            </Card>

            {/* Quick actions */}
            <section className='flex flex-col gap-3'>
                <div className='flex items-center justify-between'>
                    <h3 className='text-sm font-semibold tracking-tight'>Quick Actions</h3>
                    <Button variant='ghost' size='sm' className='text-muted-foreground' asChild>
                        <Link href='#'>View all</Link>
                    </Button>
                </div>
                <div className='grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3 xl:grid-cols-4'>
                    {actions.map(({ title, href, gradientClass, Icon }) => (
                        <Link key={title} href={href} className='group'>
                            <Card className='relative overflow-hidden rounded-2xl p-0 shadow transition-all duration-200 hover:-translate-y-1 hover:shadow-lg'>
                                <div className={`absolute inset-0 bg-gradient-to-br ${gradientClass} opacity-90`} />
                                <div className='relative flex min-h-[120px] flex-col items-center justify-center gap-3 p-4 text-white'>
                                    <Icon className='h-8 w-8 opacity-95 transition-transform duration-200 group-hover:scale-110' />
                                    <span className='px-4 text-center text-sm font-medium leading-snug'>{title}</span>
                                </div>
                            </Card>
                        </Link>
                    ))}
                </div>
            </section>

            {/* Activity and schedule */}
            <section className='grid grid-cols-1 gap-4 lg:grid-cols-3'>
                <Card className='lg:col-span-2'>
                    <CardHeader>
                        <CardTitle className='text-sm'>Recent Activity</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <ul className='space-y-4 text-sm'>
                            <li className='flex items-start gap-3'>
                                <CheckCircle2 className='mt-0.5 h-4 w-4 text-emerald-500' />
                                <p>
                                    Role <span className='font-medium'>Manager</span> updated — 2 permissions added
                                    <span className='ml-2 text-xs text-muted-foreground'>2m ago</span>
                                </p>
                            </li>
                            <li className='flex items-start gap-3'>
                                <ShieldCheck className='mt-0.5 h-4 w-4 text-blue-500' />
                                <p>
                                    Policy check passed for <span className='font-medium'>Quarterly Audit</span>
                                    <span className='ml-2 text-xs text-muted-foreground'>14m ago</span>
                                </p>
                            </li>
                            <li className='flex items-start gap-3'>
                                <Users className='mt-0.5 h-4 w-4 text-fuchsia-500' />
                                <p>
                                    12 users onboarded to <span className='font-medium'>Engineering</span>
                                    <span className='ml-2 text-xs text-muted-foreground'>1h ago</span>
                                </p>
                            </li>
                        </ul>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader>
                        <CardTitle className='text-sm'>Upcoming</CardTitle>
                    </CardHeader>
                    <CardContent className='space-y-4'>
                        <div className='flex items-center gap-3 rounded-lg border p-3'>
                            <Calendar className='h-4 w-4 text-primary' />
                            <div className='min-w-0'>
                                <p className='truncate text-sm font-medium'>Security review</p>
                                <p className='truncate text-xs text-muted-foreground'>Tomorrow, 10:30 AM</p>
                            </div>
                        </div>
                        <div className='flex items-center gap-3 rounded-lg border p-3'>
                            <Gauge className='h-4 w-4 text-primary' />
                            <div className='min-w-0'>
                                <p className='truncate text-sm font-medium'>System performance window</p>
                                <p className='truncate text-xs text-muted-foreground'>Fri, 9:00 PM</p>
                            </div>
                        </div>
                        <div className='flex items-center gap-3 rounded-lg border p-3'>
                            <Settings className='h-4 w-4 text-primary' />
                            <div className='min-w-0'>
                                <p className='truncate text-sm font-medium'>Policy refresh</p>
                                <p className='truncate text-xs text-muted-foreground'>Mon, 11:00 AM</p>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </section>
        </div>
    );
};

export default Page;
