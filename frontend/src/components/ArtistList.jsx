export default function ArtistList({ artists, onSelect }) {
  return (
    <ul>
      {artists.map((a) => (
        <li key={a.id} onClick={() => onSelect(a.id)}>
          {a.name}
        </li>
      ))}
    </ul>
  );
}
