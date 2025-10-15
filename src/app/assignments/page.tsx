import type { FC } from 'react';
import {
    Badge,
    Button,
    Card,
    CardContent,
    CardFooter,
    CardHeader,
    CardTitle
} from '@/components/ui';

type Assignment = {
    id: string;
    title: string;
    description: string;
    status: 'In Progress' | 'Completed' | 'Pending';
};

const assignments: Assignment[] = [
    {
        id: '1',
        title: 'Deploy New Feature',
        description: 'Roll out the new feature flag to 25% of users.',
        status: 'In Progress'
    },
    {
        id: '2',
        title: 'Database Migration',
        description: 'Migrate user table to new schema with zero downtime.',
        status: 'Pending'
    },
    {
        id: '3',
        title: 'Accessibility Review',
        description: 'Audit dashboard pages for WCAG AA compliance.',
        status: 'Completed'
    }
];

const getBadgeVariant = (status: Assignment['status']) => {
    switch (status) {
        case 'Completed':
            return 'secondary' as const;
        case 'In Progress':
            return 'default' as const;
        case 'Pending':
        default:
            return 'outline' as const;
    }
};

const AssignmentsPage: FC = () => {
    return (
        <div className='grid grid-cols-1 gap-6 sm:grid-cols-2 xl:grid-cols-3'>
            {assignments.map((a) => (
                <Card key={a.id} className='flex flex-col'>
                    <CardHeader>
                        <CardTitle>{a.title}</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <p className='text-sm text-muted-foreground'>{a.description}</p>
                    </CardContent>
                    <CardFooter className='mt-auto flex items-center justify-between'>
                        <Badge variant={getBadgeVariant(a.status)}>{a.status}</Badge>
                        <Button size='sm' type='button'>View Details</Button>
                    </CardFooter>
                </Card>
            ))}
        </div>
    );
};

export default AssignmentsPage;

