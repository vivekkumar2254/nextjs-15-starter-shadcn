import Link from 'next/link';
import type { FC } from 'react';

import { Card } from '@/components/ui';
import {
    Bell,
    CalendarCheck2,
    CalendarClock,
    ChartLine,
    Clock3,
    Monitor,
    FileBox,
    IdCard,
    Network,
    Bot,
    Star
} from 'lucide-react';

type Action = {
    title: string;
    colorClass: string;
    href: string;
    Icon: FC<{ className?: string }>;
};

const actions: Action[] = [
    { title: 'Org - Object Replication Monitor', Icon: Monitor, colorClass: 'bg-blue-600', href: '#' },
    { title: 'INTEGRTR HR Bot', Icon: Bot, colorClass: 'bg-pink-600', href: '#' },
    { title: 'Delegate My Workflows', Icon: CalendarCheck2, colorClass: 'bg-teal-600', href: '#' },
    { title: 'View My Profile', Icon: IdCard, colorClass: 'bg-purple-600', href: '#' },
    { title: 'View Org Chart', Icon: Network, colorClass: 'bg-zinc-600', href: '#' },
    { title: 'View Team Absences', Icon: CalendarClock, colorClass: 'bg-blue-600', href: '#' },
    { title: 'View My Time Sheet', Icon: Clock3, colorClass: 'bg-pink-600', href: '#' },
    { title: 'View Report Center', Icon: ChartLine, colorClass: 'bg-teal-600', href: '#' },
    { title: 'View Pending Workflows', Icon: FileBox, colorClass: 'bg-purple-600', href: '#' },
    { title: 'View Reminders', Icon: Bell, colorClass: 'bg-zinc-600', href: '#' },
    { title: 'View Favorites', Icon: Star, colorClass: 'bg-blue-600', href: '#' }
];

const Page: FC = () => {
    return (
        <main className='flex flex-col gap-4'>
            <h2 className='text-xl font-semibold tracking-tight'>Quick Actions</h2>
            <div className='grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3 xl:grid-cols-4'>
                {actions.map(({ title, href, colorClass, Icon }) => (
                    <Link key={title} href={href} className='group'>
                        <Card
                            className={`flex min-h-[120px] flex-col items-center justify-center gap-3 rounded-2xl text-white shadow transition-transform duration-200 ease-out hover:-translate-y-1 hover:shadow-lg ${colorClass}`}
                        >
                            <Icon className='h-8 w-8 opacity-90 transition-transform duration-200 group-hover:scale-110' />
                            <span className='px-4 text-center text-sm font-medium leading-snug'>{title}</span>
                        </Card>
                    </Link>
                ))}
            </div>
        </main>
    );
};

export default Page;
