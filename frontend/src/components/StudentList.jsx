export default function StudentList({ students, onSelect }) {
  return (
    <div>
      <h2>Students</h2>
      <ul>
        {students.map((st) => (
          <li key={st.id}>
            <button onClick={() => onSelect(st.id)}>{st.name}</button>
          </li>
        ))}
      </ul>
    </div>
  );
}
