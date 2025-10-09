export default function SongList({ songs }) {
  return (
    <div>
      <h2>Songs</h2>
      <ul>
        {songs.map((s) => (
          <li key={s.id}>{s.title}</li>
        ))}
      </ul>
    </div>
  );
}
