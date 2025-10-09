export default function ClassList({ classes, onSelect }) {
  return (
    <div>
      <h2>Classes</h2>
      <ul>
        {classes.map((cls) => (
          <li key={cls.id}>
            <button onClick={() => onSelect(cls.id)}>{cls.name}</button>
          </li>
        ))}
      </ul>
    </div>
  );
}
