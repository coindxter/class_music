export default function ClassList({ classes, onSelect }) {
  return (
    <ul>
      {classes.map((c) => (
        <li key={c.id} onClick={() => onSelect(c.id)}>
          {c.name}
        </li>
      ))}
    </ul>
  );
}
