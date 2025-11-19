'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Users } from 'lucide-react';
import { apiClient } from '@/lib/api';
import { Student } from '@/lib/types';
import StudentCard from '@/components/StudentCard';
import LoadingSpinner from '@/components/LoadingSpinner';

export default function AllStudentsPage() {
  const router = useRouter();
  const [students, setStudents] = useState<Student[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadStudents();
  }, []);

  const loadStudents = async () => {
    try {
      setLoading(true);
      const data = await apiClient.getStudents();
      setStudents(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load students');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return (
      <div className="p-8">
        <div className="glass rounded-2xl p-6 text-center">
          <p className="text-red-500">{error}</p>
          <button
            onClick={loadStudents}
            className="mt-4 px-4 py-2 glass rounded-xl hover:bg-gray-100"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <Users className="w-8 h-8 text-aura-primary" />
          <h1 className="text-3xl font-bold bg-gradient-to-r from-aura-primary to-aura-secondary bg-clip-text text-transparent">
            All Students
          </h1>
        </div>
        <p className="text-gray-600 dark:text-gray-400">
          {students.length} student{students.length !== 1 ? 's' : ''} registered
        </p>
      </div>

      {students.length === 0 ? (
        <div className="glass rounded-2xl p-12 text-center">
          <Users className="w-16 h-16 mx-auto text-gray-400 mb-4" />
          <h2 className="text-xl font-semibold text-gray-700 dark:text-gray-300 mb-2">
            No students found
          </h2>
          <p className="text-gray-500">
            Students will appear here once they are registered.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {students.map((student) => (
            <StudentCard
              key={student.student_id}
              student={student}
              onClick={() => router.push(`/admin/students/${student.student_id}`)}
            />
          ))}
        </div>
      )}
    </div>
  );
}
