export default function ArtistList({ artists, onSelect }) {
  return (
    <div>
      <h2>Artists</h2>
      <ul>
        {artists.map((a) => (
          <li key={a.id}>
            <button onClick={() => onSelect(a.id)}>{a.name}</button>
          </li>
        ))}
      </ul>
    </div>
  );
}
