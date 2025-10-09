export default function StudentList({ students, onSelect }) {
  return (
    <ul>
      {students.map((s) => (
        <li key={s.id} onClick={() => onSelect(s.id)}>
          {s.name}
        </li>
      ))}
    </ul>
  );
}
